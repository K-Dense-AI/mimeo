# Jeff Dean's Frameworks

These frameworks outline Jeff Dean's step-by-step approaches to solving complex engineering problems, from designing hardware accelerators to scaling distributed systems and vetting ML architectures.

## Back-of-the-Envelope System Design
A mental iteration process for evaluating large-scale distributed systems before writing code.
1. Identify the most important design parameters (QPS, index size).
2. Use fundamental latency and energy numbers (SRAM vs. DRAM, disk seek times) to evaluate bottlenecks.
3. Perform mental thought experiments to test how the design holds up if traffic doubles or triples.
4. Iterate mentally before committing to code.
> "I’m a big fan of thinking through designs in your head, just kind of playing with the design space a little before you actually do a lot of writing of code." (sources: src_002)

## Hardware-ML Co-design (Predicting the Puck)
A multi-year process for designing AI accelerators by predicting future ML workloads and stripping away general-purpose compute.
1. Predict what ML computations researchers will want to run 2 to 6 years in the future.
2. Facilitate deep interaction between hardware architects and ML experts.
3. Strip away general-purpose computing requirements (branchy C++ code, pointers).
4. Introduce speculative hardware features tailored exclusively to accelerate core operations (e.g., low-precision linear algebra).
> "you’re trying to predict two to six years out where, what ML computations will people want to run two to six years out in a very fast changing field." (sources: src_002, src_036)

## Model Distillation
A method to morph a large, powerful model into a smaller, cheaper model without losing significant capability.
1. Train a highly capable, large teacher model.
2. Run inputs through the teacher model to generate a probability distribution (soft targets) over the possible outputs.
3. Train a smaller student model using these soft targets, which provides a richer gradient signal than raw data.
4. Deploy the smaller model.
> "you can effectively use a powerful teacher model to make a smaller and cheaper student model from the uh you know the more sophisticated predictions that the larger model can make." (sources: src_015)

## System Design Scaling Assessment
A framework for designing new systems or evaluating their capacity to handle future growth.
1. Identify the most important design parameters (e.g., queries per second, index size).
2. Evaluate how the system will perform if traffic doubles or triples.
3. Design the system to comfortably scale by a factor of 5 or 10.
4. Avoid designing for 100x scale; instead, recognize that 100x scale will require and enable a completely new architecture.
(sources: src_033)

## 1/1000th Scale Vetting
A method for exploring a massive number of new machine learning architectures efficiently.
1. Create a 1/1000th scale version of the problem.
2. Vet hundreds of thousands of ideas or variations on that small scale.
3. Identify the approaches that seem promising.
4. Scale up only the successful ideas to medium and then large-scale production training.
> "It's very helpful to have a 1/1000th scale problem and then vet 100,000 ideas on that, and then scale up the ones that seem promising." (sources: src_026)

## Speculative Decoding
A technique for decoding from very large transformer models to improve inference efficiency and overcome memory bandwidth limits.
1. Use a fast, small drafter model to quickly generate a sequence of draft tokens (e.g., 8 tokens).
2. Have the target large model check the draft tokens in parallel.
3. Accept the correct prefix of tokens based on the large model's probability distribution.
> "you have a fast drafter model where you don't need the full sophistication of a much larger model and you can quickly generate the next say eight tokens and then have the target large model check them in parallel." (sources: src_015)

## Deterministic Replay for SDC Detection
A method for monitoring distributed ML training and detecting silent data corruption (SDC) in hardware.
1. Monitor training metrics for anomalies, such as spikes in the norm of the gradient.
2. Automatically trigger a deterministic replay of the last few training steps.
3. Compare the results: if the answers match, the spike is likely data-driven; if they differ, it indicates hardware silent data corruption.
4. Evict the defective hardware pod.
> "if we see a gradient spike, then we will effectively replay that step or the last few steps and see if we get the same answer. And if we get the same answer, we conclude, well, that's probably okay. That was probably due to the data, not due to hardware errors." (sources: src_015)
