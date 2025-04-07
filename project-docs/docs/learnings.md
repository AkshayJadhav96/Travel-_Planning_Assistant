# Learnings & Challenges

## Challenges Faced
1. **Latency Issues**: Tool execution took longer than expected.
2. **API Limitations**: Faced challenges in finding suitable APIs due to rate limits or request restrictions, which led to modifying certain functionalities or settling for alternatives with reduced capabilities.
3. **LLM Decision-Making**: Ensuring the LLM correctly picks the right tools.
4. **Trial and error**: Tried different LLMs to check which is performing better tool use (e.g. Llama3.2,Qwen2.5:3b)

## Key Learnings
- **Optimized API Calls**: Reduced unnecessary API requests by caching responses.
- **Efficient Tool Invocation**: Improved tool execution by refining prompt engineering.
- **Enhanced Logging**: Added debugging logs for better issue tracking.
