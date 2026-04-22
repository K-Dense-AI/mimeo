"""Pydantic schemas for the pipeline."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


SourceKind = Literal[
    "essay",
    "talk",
    "interview",
    "podcast",
    "book",
    "paper",
    "letter",
    "other",
]
SourceMedium = Literal["web", "youtube", "audio", "research-report"]


class Source(BaseModel):
    """A single discovered source to process."""

    id: str = Field(description="Stable id like src_001; order of discovery.")
    url: str
    title: str | None = None
    publish_date: str | None = None
    kind: SourceKind = "other"
    medium: SourceMedium = "web"
    bucket: str | None = Field(
        default=None,
        description="Which discovery bucket this came from (essays, talks, etc.).",
    )
    excerpts: list[str] = Field(default_factory=list)
    canonicity_score: float | None = Field(
        default=None,
        description="LLM-assigned 0-1 score; higher = more canonical / primary / long-form.",
    )


class FetchedContent(BaseModel):
    """Raw text extracted from a source, post-fetch."""

    source_id: str
    url: str
    title: str | None
    text: str
    char_count: int
    fetch_method: str = Field(description="parallel-excerpt | parallel-extract | trafilatura | youtube-captions | whisper")
    language: str | None = None


class Principle(BaseModel):
    """A belief or rule the expert endorses."""

    statement: str = Field(description="The principle, in their voice if possible.")
    rationale: str = Field(description="Why they believe it.")
    source_quote: str | None = Field(
        default=None, description="A short verbatim quote grounding the principle."
    )
    source_id: str = Field(description="The source this was extracted from.")


class Framework(BaseModel):
    """A named repeatable procedure."""

    name: str
    when_to_apply: str
    steps: list[str] = Field(default_factory=list)
    source_quote: str | None = None
    source_id: str


class MentalModel(BaseModel):
    """A reasoning pattern / metaphor / lens."""

    name: str
    description: str
    example: str | None = None
    source_id: str


class Quote(BaseModel):
    """A signature quote with attribution."""

    text: str
    context: str | None = None
    source_id: str


class AntiPattern(BaseModel):
    """Something the expert explicitly warns against."""

    description: str
    why_it_fails: str | None = None
    source_id: str


class Extraction(BaseModel):
    """What a single-source distillation call returns."""

    source_id: str
    summary: str = Field(description="2-4 sentence summary of the source.")
    themes: list[str] = Field(default_factory=list)
    principles: list[Principle] = Field(default_factory=list)
    frameworks: list[Framework] = Field(default_factory=list)
    mental_models: list[MentalModel] = Field(default_factory=list)
    heuristics: list[str] = Field(default_factory=list)
    signature_quotes: list[Quote] = Field(default_factory=list)
    anti_patterns: list[AntiPattern] = Field(default_factory=list)


class RankedSources(BaseModel):
    """Wrapper for the LLM ranking step."""

    sources: list[Source]


class ExpertCandidate(BaseModel):
    """One possible real-world referent for an ambiguous expert name."""

    name: str = Field(description="The name as typically rendered.")
    description: str = Field(
        description=(
            "A short qualifier that distinguishes this person from "
            "namesakes, e.g. 'co-founder of AngelList, investor'."
        )
    )
    evidence: str | None = Field(
        default=None,
        description="One-line rationale grounded in the search evidence.",
    )


class IdentityResolution(BaseModel):
    """Result of the identity-disambiguation pre-flight.

    When ``is_ambiguous`` is ``False`` the single best match's qualifier is in
    ``resolved_description``. When ``is_ambiguous`` is ``True`` the caller
    must either prompt the user to pick from ``candidates`` or fail loudly so
    downstream stages don't silently blend multiple people's work.
    """

    is_ambiguous: bool = Field(
        description="True only when 2+ notable people plausibly share this name."
    )
    resolved_description: str | None = Field(
        default=None,
        description=(
            "Short qualifier for the single match when unambiguous "
            "(e.g. 'co-founder of AngelList, investor, essayist'). "
            "Null when ambiguous."
        ),
    )
    candidates: list[ExpertCandidate] = Field(
        default_factory=list,
        description="2-5 candidates when ambiguous; empty when not.",
    )
    notes: str | None = None


class ClusteredItem(BaseModel):
    """A deduplicated concept merged across sources."""

    label: str = Field(description="Canonical name for the concept.")
    summary: str = Field(description="Unified description.")
    details: str | None = Field(
        default=None, description="Extra context - steps, rationale, examples."
    )
    representative_quote: str | None = None
    source_ids: list[str] = Field(default_factory=list)

    @property
    def frequency(self) -> int:
        return len(self.source_ids)


class ClusteredCorpus(BaseModel):
    """Cross-source merged corpus used by the synthesize step.

    Each list entry represents a *merged* concept. ``source_ids`` lists every
    source that mentioned it (for frequency + attribution).
    """

    expert_name: str
    themes: list[str] = Field(default_factory=list)
    principles: list[ClusteredItem] = Field(default_factory=list)
    frameworks: list[ClusteredItem] = Field(default_factory=list)
    mental_models: list[ClusteredItem] = Field(default_factory=list)
    heuristics: list[ClusteredItem] = Field(default_factory=list)
    signature_quotes: list[ClusteredItem] = Field(default_factory=list)
    anti_patterns: list[ClusteredItem] = Field(default_factory=list)


class SkillOutput(BaseModel):
    """Final authored skill content ready to write to disk."""

    skill_name: str
    description: str = Field(
        description="Skill-creator style trigger description (frontmatter)."
    )
    skill_body: str = Field(description="Markdown body of SKILL.md (after frontmatter).")
    principles_md: str
    frameworks_md: str
    mental_models_md: str
    quotes_md: str
    heuristics_md: str = Field(
        default="",
        description=(
            "Markdown for references/heuristics.md: pithy rules of thumb the "
            "expert applies day-to-day."
        ),
    )
    anti_patterns_md: str = Field(
        default="",
        description=(
            "Markdown for references/anti-patterns.md: things the expert "
            "explicitly warns against, each with a short 'why it fails'."
        ),
    )


class AgentsOutput(BaseModel):
    """Final authored AGENTS.md content, a single always-on markdown file."""

    content: str = Field(
        description="Full AGENTS.md file content, ready to write verbatim."
    )


class QuoteVerification(BaseModel):
    """Result of checking one clustered quote against its source text(s)."""

    category: Literal[
        "principles",
        "frameworks",
        "mental_models",
        "heuristics",
        "signature_quotes",
        "anti_patterns",
    ]
    label: str = Field(description="The clustered item's label (for reporting).")
    quote: str
    source_ids: list[str]
    verified: bool
    matched_source_id: str | None = Field(
        default=None,
        description="The specific source id whose text contained the quote.",
    )
    match_ratio: float = Field(
        default=0.0,
        description=(
            "0-1 similarity score for the best candidate window. 1.0 on an "
            "exact substring match; lower values are fuzzy matches."
        ),
    )


class VerificationReport(BaseModel):
    """Aggregate verification result for a corpus."""

    total: int = 0
    verified: int = 0
    unverified: list[QuoteVerification] = Field(default_factory=list)
    # We keep the full verification record for the audit trail; callers that
    # only want unverified ones filter themselves.
    all_results: list[QuoteVerification] = Field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 1.0
        return self.verified / self.total


class CritiqueIssue(BaseModel):
    """A single problem the critique step found with the authored skill."""

    severity: Literal["high", "medium", "low"]
    category: Literal[
        "voice",
        "duplication",
        "unattributed",
        "vagueness",
        "structure",
        "coverage",
        "other",
    ]
    location: str = Field(
        description=(
            "Short pointer to where the issue lives, e.g. 'SKILL.md > Core "
            "principles' or 'references/frameworks.md'."
        )
    )
    description: str
    suggestion: str | None = None


class CritiqueReport(BaseModel):
    """LLM critique of an authored skill or AGENTS.md."""

    overall_score: int = Field(
        description="0-10 holistic score. 10 = ready to ship, 0 = unusable."
    )
    summary: str = Field(description="2-4 sentence overall assessment.")
    issues: list[CritiqueIssue] = Field(default_factory=list)
    strengths: list[str] = Field(
        default_factory=list,
        description="Short bullets naming what the skill got right.",
    )
