# Jeff Dean's Heuristics

These are the pithy rules of thumb and operational heuristics Jeff Dean applies day-to-day when evaluating systems, research, and engineering trade-offs.

## Bigger Model, More Data
Bigger model, more data, better results. This is the mantra that drove Google's neural network scaling efforts for years.
> "Bigger model, more data, better results." (sources: src_015, src_033)

## Back-of-the-Envelope First
Do back-of-the-envelope calculations before writing code to understand fundamental limits.
> "I’m a big fan of thinking through designs in your head, just kind of playing with the design space a little before you actually do a lot of writing of code." (sources: src_002)

## Scale by 10x, Not 100x
Design systems to scale by factors of 5 or 10, but probably not beyond that, as 100x requires a new architecture.
> "you're want to design a system so that the most important characteristics could scale by like factors of five or 10 but probably not beyond that" (sources: src_033)

## Low Precision for Energy Savings
Use very low precision (7 or 8 bits) for neural network inference to save energy on data transfer. Because it's joules per bit transferred, reducing bit precision saves a tremendous amount of energy.
> "I'm a big fan of very low precision because I think that gets that saves you a tremendous amount of energy, right? Because it's joules per bit that you're transferring." (sources: src_015, src_033)

## Read 100 Abstracts
Read 100 abstracts instead of deeply reading one paper to connect the dots across fields and understand the highest-level concepts.
> "I think you would be much better served to take the time to read 100 abstracts of 100 different papers and sort of understand the highest level concept that they each have." (sources: src_036)

## Evaluate Utility over Perfect Factuality
Evaluate an AI model's utility based on the specific task's need for exact factuality. Don't block useful features (like creative writing or coding) just because the model isn't perfectly factual for search queries.
> "It’s a hard problem and even though these models are not factual all the time – they are still useful." (sources: src_018)

## Partner for Knowledge
The way to do interesting things is to partner with people who know things you don't.
> "a really good way to do interesting things is to partner with people who know things that you don't." (sources: src_036)

## Predict Workloads 2-6 Years Out
Predict ML workloads 2-6 years out when co-designing hardware, since hardware takes years to design and deploy.
(sources: src_002, src_030)

## Diminishing Returns on Benchmarks
Benchmarks are most useful when initial scores are 10-30%; once they hit 95%, you get diminishing returns and risk overfitting.
(sources: src_033)

## Don't Hype Unfinished Work
Don't hype things that aren't done yet.
> "I just don't like to hype things that aren't done yet." (sources: src_026)
