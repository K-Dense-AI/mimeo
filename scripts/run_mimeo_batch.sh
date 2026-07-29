#!/usr/bin/env bash
# Run mimeo sequentially over a curated list of the top 20 AI scientists
# (deep learning, reinforcement learning, NLP, computer vision, robotics).
#
# Usage:
#   ./scripts/run_mimeo_batch.sh                # default: --format both (SKILL.md + AGENTS.md)
#   FORMAT=skill ./scripts/run_mimeo_batch.sh   # emit only SKILL.md
#   FORMAT=agents ./scripts/run_mimeo_batch.sh  # emit only AGENTS.md
#   EXTRA_ARGS="--max-sources 40 --deep-research" ./scripts/run_mimeo_batch.sh
#
# On error the script keeps going to the next name and records the failure
# in the log file. Per-name output lives under ./output/<slug>/ and shared
# intermediates are cached under each skill's _workspace/ so re-runs are cheap.

set -u
set -o pipefail

cd "$(dirname "$0")/.."

FORMAT="${FORMAT:-both}"
EXTRA_ARGS="${EXTRA_ARGS:-}"
LOG_DIR="logs"
mkdir -p "$LOG_DIR"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
LOG_FILE="$LOG_DIR/mimeo-batch-$TIMESTAMP.log"

# Format: "Full Name|short disambiguator to pin the right person"
# Disambiguators help mimeo's identity step lock onto the correct individual
# without an interactive prompt.
PEOPLE=(
  # --- Top 20 AI Scientists ---
  "Geoffrey Hinton|deep learning pioneer, backpropagation, University of Toronto, 2018 Turing Award"
  "Yann LeCun|deep learning, convolutional neural networks, Chief AI Scientist at Meta, NYU, 2018 Turing Award"
  "Yoshua Bengio|deep learning, Mila Quebec AI Institute, Université de Montréal, 2018 Turing Award"
  "Andrej Karpathy|deep learning, former Director of AI at Tesla, founding member of OpenAI, Eureka Labs"
  "Ilya Sutskever|deep learning, co-founder of OpenAI and Safe Superintelligence Inc., AlexNet co-author"
  "Andrew Ng|machine learning, co-founder of Coursera and DeepLearning.AI, Stanford University, former Google Brain lead"
  "Demis Hassabis|CEO and co-founder of Google DeepMind, AlphaGo and AlphaFold, 2024 Nobel Prize in Chemistry"
  "Fei-Fei Li|computer vision, ImageNet creator, Stanford University, co-director of Stanford HAI, World Labs"
  "Ian Goodfellow|inventor of Generative Adversarial Networks (GANs), DeepMind"
  "Jürgen Schmidhuber|LSTM co-inventor, IDSIA Switzerland, KAUST, deep learning pioneer"
  "Richard S. Sutton|reinforcement learning pioneer, University of Alberta, Keen Technologies, 2024 Turing Award"
  "Judea Pearl|causality and Bayesian networks, UCLA, 2011 Turing Award"
  "Stuart Russell|AI safety, UC Berkeley, co-author of 'Artificial Intelligence: A Modern Approach'"
  "Pieter Abbeel|robotics and reinforcement learning, UC Berkeley, co-founder of Covariant"
  "Daphne Koller|machine learning, co-founder of Coursera, founder and CEO of Insitro, Stanford University"
  "Jeff Dean|Chief Scientist at Google DeepMind and Google Research, co-creator of TensorFlow and MapReduce"
  "David Silver|reinforcement learning, lead researcher on AlphaGo and AlphaZero at DeepMind, UCL"
  "Kaiming He|computer vision, ResNet creator, MIT, formerly Meta AI (FAIR)"
  "Christopher Manning|natural language processing, Stanford University, director of Stanford AI Lab"
  "Sebastian Thrun|robotics and self-driving cars, founder of Google X, Waymo, Udacity, Stanford University"
)

total="${#PEOPLE[@]}"
count=0
succeeded=0
failed=0
skipped=0

echo "mimeo batch run starting: $total names, format=$FORMAT" | tee -a "$LOG_FILE"
echo "Logging to $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

slugify() {
  # Transliterate accented characters to ASCII (e.g. ü -> u, é -> e) so
  # "Jürgen Schmidhuber" becomes "jurgen-schmidhuber" rather than
  # "j-rgen-schmidhuber". Uses python3 (already required by `uv run`)
  # because macOS iconv and BSD sed can't do this portably.
  printf '%s' "$1" | python3 -c '
import sys, unicodedata, re
s = unicodedata.normalize("NFKD", sys.stdin.read())
s = "".join(c for c in s if not unicodedata.combining(c))
print(re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-"))
'
}

for entry in "${PEOPLE[@]}"; do
  count=$((count + 1))
  name="${entry%%|*}"
  disambig="${entry#*|}"
  slug="$(slugify "$name")"

  header="[$count/$total] $name"
  echo "================================================================" | tee -a "$LOG_FILE"
  echo "$header" | tee -a "$LOG_FILE"
  echo "disambiguator: $disambig" | tee -a "$LOG_FILE"
  echo "slug: $slug" | tee -a "$LOG_FILE"

  # Skip only when all required artefacts for this format already exist.
  skip=0
  case "$FORMAT" in
    skill)
      marker="output/$slug/SKILL.md"
      [[ -f "output/$slug/SKILL.md" ]] && skip=1
      ;;
    agents)
      marker="output/$slug/AGENTS.md"
      [[ -f "output/$slug/AGENTS.md" ]] && skip=1
      ;;
    both)
      marker="output/$slug/{SKILL.md,AGENTS.md}"
      if [[ -f "output/$slug/SKILL.md" && -f "output/$slug/AGENTS.md" ]]; then
        skip=1
      fi
      ;;
    *)
      marker="output/$slug/SKILL.md"
      [[ -f "output/$slug/SKILL.md" ]] && skip=1
      ;;
  esac

  if [[ "$skip" -eq 1 ]]; then
    echo "-> already built ($marker), skipping" | tee -a "$LOG_FILE"
    skipped=$((skipped + 1))
    echo "" | tee -a "$LOG_FILE"
    continue
  fi

  start_ts=$(date +%s)
  # shellcheck disable=SC2086  # EXTRA_ARGS is intentionally word-split
  if uv run mimeo "$name" \
      --format "$FORMAT" \
      --disambiguator "$disambig" \
      $EXTRA_ARGS 2>&1 | tee -a "$LOG_FILE"; then
    elapsed=$(( $(date +%s) - start_ts ))
    echo "-> ok (${elapsed}s)" | tee -a "$LOG_FILE"
    succeeded=$((succeeded + 1))
  else
    elapsed=$(( $(date +%s) - start_ts ))
    echo "-> FAILED (${elapsed}s) on $name" | tee -a "$LOG_FILE"
    failed=$((failed + 1))
  fi
  echo "" | tee -a "$LOG_FILE"
done

echo "================================================================" | tee -a "$LOG_FILE"
echo "Batch complete: $succeeded ok, $failed failed, $skipped skipped, $total total" | tee -a "$LOG_FILE"
echo "Log: $LOG_FILE" | tee -a "$LOG_FILE"

exit $(( failed > 0 ? 1 : 0 ))
