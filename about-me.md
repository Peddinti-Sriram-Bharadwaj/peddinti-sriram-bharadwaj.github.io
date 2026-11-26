# Peddinti Sri Ram Bharadwaj

**AI/RL Researcher & Systems Engineer**

Reinforcement learning, self-play, and the systems underneath — from measure-theoretic RL theory down to Vulkan compute shaders on Android.

- Email: PeddintiSri.Ram@iiitb.ac.in
- GitHub: https://github.com/Peddinti-Sriram-Bharadwaj
- LinkedIn: https://www.linkedin.com/in/sriram-bharadwaj-p/

## About

M.Tech in Computer Science at IIIT Bangalore, currently researching continual self-play reinforcement learning for LLM post-training and plasticity collapse. Work spans RL theory (SOR family, dormant neurons, measure-theoretic unlearning vulnerabilities), generative vision (ControlNet, diffusion), and low-level systems (Vulkan compute on Android, PyTorch/ExecuTorch build internals).

## Experience

- **Independent Researcher** — Remote, Aug 2026 – Present
  Continual self-play RL for LLM post-training; unified multi-agent RL framework across TextArena, OpenSpiel, PettingZoo, JaxMARL; dual-LoRA adversarial self-play for code repair.
- **Research Intern, Stochastic Systems Lab** — IISc, Jan – Jul 2026
  Co-developed the SOR family of parametrized Bellman target-update rules via Successive Over-Relaxation; ran massively parallel GPU sweeps across 8 GPUs; manuscript under review.
- **Freelance Agentic AI Engineer** — Remote, Feb – Apr 2025
  Architected an end-to-end NLU agentic system on LangGraph with prompt-injection guardrails, deployed via scalable FastAPI endpoints.

## Projects

- **UBU: Unmeasurability-Based Unlearning for Safe Reinforcement Learning** — with Prof. Raghuram Bharadwaj, IIIT Bangalore (Oct 2025, revised Aug 2026). Supermartingale/Carathéodory reconstruction attack on RL unlearning; defence via σ-contractive (sparse MoE) representations that make forbidden states unmeasurable. Attack IoU >0.95 → <0.05. PDF on the site: assets/papers/ubu-unlearning-safe-rl.pdf

- **Tacit Collusion in Pricing Agents: Robustness, Detection, and a Mechanistic Probe of a Pricing LLM** — Apart Research AI Collusion Research Sprint, Oct 2026 (team "Code Compels", with Chewon Cho and Gagana MD). Finds that a single agent refusing high prices breaks collusion, that steering a pricing LLM's internal representation moves its own price, and that it shows no punishment of undercutting rivals. — https://apartresearch.com/sprints/projects/tacit-collusion-in-pricing-agents-robustness-detection-and-a-mechanistic-probe-of-a-pricing-llm-qxsb · https://github.com/Peddinti-Sriram-Bharadwaj/Collusion
- **The SOR Family: A Navigable Continuum of Bellman Training Signals** for Deep Reinforcement Learning (with Prof. Raghuram Bharadwaj, IIIT Bangalore, and Prof. Shalabh Bhatnagar, IISc; under review) — SOR on the Bellman target converges to Q_ω = ωQ* + (1−ω)V*: same optimal policy, action gaps scaled by ω. Speed gains are largely absorbed by a tuned learning rate in deep Q-learning; safe ω from the model converges on all 72 MDPs and 36 games in planning. Classic control + MinAtar. *(RL theory, PyTorch, Optuna)*
- **Continual Self-Play RL (Qwen2.5)** — Multi-agent self-play framework unifying REINFORCE, REINFORCE++, DAPO, and GRPO to study plasticity collapse in non-stationary environments. *(RL, LLM post-training, Multi-agent)*
- **Dormant Neurons in RL** — Tracks post-ReLU activation dormancy in RL policy networks; introduces Zero-Interference Routing (ZIR) as an architectural fix. *(RL, PyTorch)* — https://github.com/Peddinti-Sriram-Bharadwaj/dormat_RL
- **Monte Carlo Tree Search Suite** — Classical MCTS through a full AlphaZero implementation in JAX/Flax NNX, including a Neural SOR variant applying Successive Over-Relaxation. *(MCTS, JAX, AlphaZero)* — https://github.com/Peddinti-Sriram-Bharadwaj/MCTS
- **Parallel Tree Reduction Engine (Android)** — Vulkan Compute / NDK hybrid Kotlin-C++ app offloading tree-reduction arithmetic to the GPU with manual memory synchronization. *(Vulkan, Android NDK, GPGPU)* — https://github.com/Peddinti-Sriram-Bharadwaj/GpuComputeTest
- **QnAOps** — Horizontally scalable LLM Q&A platform, load-tested to 30 concurrent pods, with zero-touch Jenkins CI/CD and ELK observability. *(MLOps, Kubernetes, LLM serving)* — https://github.com/Peddinti-Sriram-Bharadwaj/QnaOps

## Education

- M.Tech, Computer Science & Engineering — IIIT Bangalore, 2024–2026
- B.Tech, Computer Science & Engineering — GITAM Institute of Technology, Visakhapatnam, 2020–2024

## Interests

- Photography (gallery page on the site, photos to be added)
- Absurdist philosophy (Camus)

## Certifications

- **AGI Strategy** — BlueDot Impact

## Reading

- *The Stranger* — Albert Camus (read)
- *The Myth of Sisyphus* — Albert Camus (reading)

## Writing

- Substack: https://substack.com/@srirambharadwaj
- "What is it about arts that makes it so 'human'" — handwritten essay, 17 Nov 2026

## Skills

PyTorch · JAX / Flax · Reinforcement Learning · Measure-theoretic probability · Vulkan / GPGPU · Kubernetes · LangGraph / Agentic AI · C++ / Android NDK
