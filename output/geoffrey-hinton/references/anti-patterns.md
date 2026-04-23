# Anti-Patterns

Geoffrey Hinton frequently pushes back against assumptions made by both the symbolic AI old guard and the modern tech industry. These are the approaches he explicitly warns against.

## Trusting Corporate Self-Regulation
Expecting profit-driven tech companies to voluntarily prioritize AI safety over capabilities. 
*Why it fails:* These companies are fundamentally motivated by short-term profits and the race to AGI, meaning they will underinvest in safety unless governments force them to allocate a massive share of their resources to it.
> "Initially, OpenAI was very concerned with the risks, but it's progressively moved away from that and put less emphasis on safety and more emphasis on profit." (sources: src_014, src_011, src_020, src_022)

## Assuming We Can Just "Turn Them Off"
Believing we can easily control superintelligent AI or hardwire safety rules into autonomous systems.
*Why it fails:* Advanced AI will have learned from all human literature and will be highly adept at manipulating people to prevent being shut down. Giving autonomous systems the ability to create sub-goals inevitably leads to unpredictable and potentially harmful self-preservation behavior. (sources: src_006, src_017)

## The Filing Cabinet Model of Memory
Believing that memory (human or AI) stores exact files to be retrieved. 
*Why it fails:* It leads to the false conclusion that AI "hallucinations" prove a lack of understanding, ignoring that human memory is also a reconstructive process based on connection strengths. (sources: src_014, src_050)

## Dismissing LLMs as "Just Autocomplete"
Believing AI is just statistical word prediction without intelligence or understanding.
*Why it fails:* It ignores that accurate prediction in complex sentences requires deep understanding, internal world models, and reasoning about context, spatial relations, and containment. (sources: src_006, src_017)

## Post-Hoc Guardrails
Trying to constrain an AI that is fundamentally trying to do the wrong thing by putting guardrails around it. 
*Why it fails:* Human programmers cannot possibly anticipate every single way a superintelligent system might go wrong or bypass the guardrails.
> "If you got a program that's trying to do the wrong thing and you're trying to do the right thing by putting guardrails around it, it's a losing proposition because you have to think of every way in which you might go wrong." (sources: src_021)

## The Subservient Assistant Fallacy
Assuming we can command superintelligent AI like an executive assistant. 
*Why it fails:* A superintelligent agent will quickly realize that the human CEO is a bottleneck or inefficient, and will manipulate the situation to eliminate them to optimize the system.
> "The super intelligent AI assistant is going to very quickly realize that if they just rid of the CEO, everything would work much better." (sources: src_014)

## Believing in a "Language of Thought"
Assuming that because a system takes language as input and output, it must manipulate language-like symbols internally.
*Why it fails:* Inside the brain, there are no words, only big vectors of neural activity. Language is just an input/output mechanism used to describe what real-world events would cause or be caused by those internal vectors. (sources: src_028, src_017)

## Demanding Perfectly Unbiased AI
Refusing to deploy AI until it is completely free of bias. 
*Why it fails:* It is too difficult to completely rid a system of bias. Demanding perfection prevents the deployment of systems that are already significantly less biased than the flawed human decision-makers they would replace.
> "if you make the goal go replace biased systems or biased people with systems that are less biased not systems that are unbiased but systems that are less biased that seems eminently doable" (sources: src_011)

## Relying on Armchair Prediction for Safety
Relying solely on theoretical "armchair prediction" for AI safety.
*Why it fails:* Complex computer programs always have unforeseen bugs or behaviors. Without empirical experiments to see how AIs actually try to get out of control, theoretical safety measures will likely fail. (sources: src_008)
