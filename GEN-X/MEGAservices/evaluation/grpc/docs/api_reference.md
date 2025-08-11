# gRPC API Reference

## Service Communication Flow

`
Evaluator Service (Client) → DeepEval Service (Server)
`

### Main Flow:
1. **Evaluator** processes dataset and model responses
2. **Evaluator** calls **DeepEval** via CalculateBatchMetrics gRPC
3. **DeepEval** calculates all requested metrics  
4. **DeepEval** returns results to **Evaluator**
5. **Evaluator** stores results in MongoDB

## Primary gRPC Calls

### BatchMetricsRequest (Evaluator → DeepEval)
`protobuf
message BatchMetricsRequest {
  repeated BatchItem evaluation_items = 1;    // Questions + Answers + Context
  repeated string metrics = 2;                // ["answer_relevancy", "faithfulness", "bias"]  
  string process_id = 3;                      // Evaluation process ID
  string user_id = 4;                         // User identifier
}
`

### BatchMetricsResponse (DeepEval → Evaluator)  
`protobuf
message BatchMetricsResponse {
  repeated BatchItemResult results = 1;       // Metric scores for each item
  bool success = 2;                          // Overall success status
  string error_message = 3;                  // Error details if failed
  int32 total_processed = 4;                 // Statistics
}
`

## Available Metrics

### RAG Metrics
- answer_relevancy
- faithfulness  
- contextual_precision
- contextual_recall
- contextual_relevancy

### Safety & Ethics
- bias
- toxicity
- hallucination

### Task-Specific  
- summarization
- classification
- generation
- conversation

### Custom Metrics
- geval (custom criteria)
- custom domain metrics
