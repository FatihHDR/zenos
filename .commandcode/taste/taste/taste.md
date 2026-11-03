# Taste
- Writes in Indonesian and expects responses in Indonesian (Bahasa Indonesia), not English. Confidence: 0.9
- Communicates in terse, minimal-direction commands (e.g. a single "lanjutkan"/"continue" or "kerjakan yang phase 4, point 1 dan 2") and trusts the agent to keep executing autonomously without further hand-holding. Confidence: 0.6
- Produces formal Indonesian academic writing about their projects (thesis/journal-style) and expects the standard Indonesian research structure — judul, then BAB I with Latar Belakang, Rumusan Masalah, Tujuan, Manfaat, and Batasan Masalah. Confidence: 0.55
- Expects research titles/introductions to explicitly state what is studied, the data used, and the method used. Confidence: 0.6
- Follows a formal multi-chapter (BAB I–V) thesis/proposal template and expects each chapter to conform to its prescribed subsections when asked to draft it. Confidence: 0.6
- Uses IEEE numeric citation style (numbering continuous across the whole document, not restarted per chapter) and the Mendeley reference manager for academic citations. Confidence: 0.6
- Expects strict academic separation of content: conceptual theory and literature in Bab 2, while dataset specifics, hyperparameters, model configuration, and experimental results belong in Bab 3; frowns on duplicate/irrelevant general definitions. Confidence: 0.55
- For writing/document deliverables (proposals, thesis chapters, write-ups), prefers long, elaborative, detailed prose and will explicitly ask to expand when the draft is too short — favor thorough multi-section output over concise summaries. Confidence: 0.55
- Prefers the agent to perform setup/configuration autonomously via its tools (driving APIs, running docker/CLI itself) instead of being handed manual click-through or step-by-step dashboard instructions. Confidence: 0.6
- Prefers gRPC over REST for Qdrant client connections (`prefer_grpc=True`). Confidence: 0.7
- Cost-conscious about LLM API choices: actively looks for cheaper alternatives to Anthropic, and is open to OpenAI-compatible routers/endpoints (e.g. 9router, OpenRouter, Groq, Ollama) as drop-in providers. Often reaches for free / no-auth options first (e.g. OpenCode Free). Confidence: 0.7
- Prioritizes reaching practical usage over exhaustive verification: explicitly told the agent "no need for test suite" to skip running the full test suite and move on to how-to-use guidance. Confidence: 0.5
- Works PRD-first: maintains a PRD.md in the project and expects the agent to read it and cross-check implementation against it (listing what's done vs not done) rather than inventing scope. Confidence: 0.5
- Asks terse follow-up questions about how/why things work (e.g. "db nya gimana", "kalo ini maksudnya gimana", "itu buat apa") and expects a conceptual explanation, not just the command to run. Confidence: 0.5
- Deploys (or plans to deploy) to their own single-node VPS, but is still drawn to container orchestration — proactively asks whether Kubernetes is in/out of scope and chooses to run the stack on Kubernetes (k3s/kind) even for a single node, accepting manual manifest work (StatefulSet/PVC, NodePort, image loading) to get there. Confidence: 0.5
- Pastes secret credentials (API keys, dashboard passwords) directly into chat rather than storing them first, expecting the agent to wire them into config files / Secrets. Confidence: 0.5
nya gimana", "itu buat apa") and expects a conceptual explanation, not just the command to run. Confidence: 0.5
