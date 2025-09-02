# AWS Bedrock Agent Template

This repository contains a CloudFormation template for creating an AWS Bedrock Agent configured with Claude Sonnet 3.7 for testing with OpenWebUI.

## Template Overview

The `bedrock-agent-template.yaml` file creates:

- **Bedrock Agent** with Claude Sonnet 3.7 foundation model
- **IAM Role** with necessary permissions for the agent
- **Agent Alias** for invoking the agent
- **CloudWatch Log Group** for monitoring agent activity
- **Custom prompt configurations** optimized for testing scenarios

## Key Features

### Foundation Model Support
- **Primary**: Claude Sonnet 3.7 (anthropic.claude-3-5-sonnet-20241022-v2:0)
- **Alternatives**: Claude 3.5 Haiku, Claude 3 Sonnet/Haiku (configurable)

### Agent Configuration
- **Idle Session TTL**: 3600 seconds (1 hour)
- **Custom Instructions**: Pre-configured for helpful AI assistant behavior
- **Prompt Overrides**: Separate configurations for preprocessing and orchestration

### Security & Monitoring
- **IAM Role**: Least-privilege permissions for Bedrock operations
- **CloudWatch Logging**: Automatic log group creation with 30-day retention
- **Parameter Store**: Environment-based configuration

## Template Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `AgentName` | TestAgent | Name of the Bedrock Agent |
| `AgentDescription` | Bedrock Agent for OpenWebUI testing... | Description of the agent |
| `FoundationModel` | anthropic.claude-3-5-sonnet-20241022-v2:0 | Claude model to use |
| `Environment` | dev | Deployment environment (dev/test/prod) |

## Customizing the Template

### Modifying Agent Instructions

Edit the `Instruction` property in the `BedrockAgent` resource:

```yaml
Instruction: |
  You are a specialized AI assistant for [your use case].
  Your capabilities include:
  - [List specific capabilities]
  - [Add domain-specific instructions]
```

### Adding Action Groups

To add Lambda-based action groups, add a new resource:

```yaml
MyActionGroup:
  Type: AWS::Bedrock::AgentActionGroup
  Properties:
    AgentId: !Ref BedrockAgent
    ActionGroupName: MyActionGroup
    Description: Description of the action group
    ActionGroupExecutor:
      Lambda: !GetAtt MyLambdaFunction.Arn
    FunctionSchema:
      # Define your function schema here
```

### Updating Foundation Model

Change the `FoundationModel` parameter to use different Claude models:

- **Claude 3.5 Sonnet**: `anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Claude 3.5 Haiku**: `anthropic.claude-3-5-haiku-20241022-v2:0`
- **Claude 3 Sonnet**: `anthropic.claude-3-sonnet-20240229-v1:0`
- **Claude 3 Haiku**: `anthropic.claude-3-haiku-20240307-v1:0`

### Custom Prompt Templates

Modify the `PromptOverrideConfiguration` to customize agent behavior:

```yaml
PromptOverrideConfiguration:
  PromptConfigurations:
    - PromptType: ORCHESTRATION
      BasePromptTemplate: |
        Your custom orchestration prompt here...
      InferenceConfiguration:
        Temperature: 0.7  # Adjust creativity (0.0-1.0)
        TopP: 0.9        # Adjust diversity
        TopK: 250        # Adjust token selection
        MaximumLength: 2000  # Max response length
```

## OpenWebUI Integration

### Prerequisites
1. Deploy the CloudFormation stack
2. Note the Agent ID and Alias ID from stack outputs
3. Configure OpenWebUI to use AWS Bedrock

### Testing with OpenWebUI

1. **Configure OpenWebUI** to connect to your Bedrock agent
2. **Use the Agent Alias ARN** for API calls
3. **Monitor logs** in CloudWatch for debugging

### Sample API Call

```bash
aws bedrock-agent-runtime invoke-agent \
  --agent-id YOUR_AGENT_ID \
  --agent-alias-id YOUR_ALIAS_ID \
  --session-id "test-session-123" \
  --input-text "Hello! Can you help me test this agent?" \
  --region YOUR_REGION
```

## Template Validation

Validate the CloudFormation template before deployment:

```bash
aws cloudformation validate-template --template-body file://bedrock-agent-template.yaml
```

## Cost Optimization

### Model Selection
- **Claude 3.5 Sonnet**: Best for complex reasoning tasks
- **Claude 3.5 Haiku**: Cost-effective for simpler tasks

### Session Management
- **IdleSessionTTLInSeconds**: Adjust based on usage patterns
- **Log Retention**: Set to 7 days for dev, 30+ for prod

## Troubleshooting

### Common Issues

1. **Model Access**: Ensure the foundation model is enabled in your AWS account
2. **IAM Permissions**: Verify the agent role has necessary permissions
3. **Region Availability**: Check if Bedrock services are available in your region

### Debugging
- Check CloudWatch logs: `/aws/bedrock/AgentName-Environment`
- Use AWS Bedrock console to test agent directly
- Validate template syntax with `cfn-lint`

## Development Workflow

1. **Edit Template**: Modify `bedrock-agent-template.yaml`
2. **Validate**: Run template validation
3. **Test**: Deploy to dev environment first
4. **Iterate**: Make changes based on testing results
5. **Deploy**: Promote to production when ready

## Security Considerations

- **IAM Roles**: Uses least-privilege principle
- **Logging**: All agent interactions are logged
- **Encryption**: Data is encrypted at rest and in transit
- **Access Control**: Restrict agent access based on your requirements

## Contributing

When modifying this template:
1. Keep parameters configurable
2. Add comments for complex configurations
3. Test in multiple environments
4. Update this README with changes

## Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [CloudFormation Best Practices](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html)
- [OpenWebUI Documentation](https://docs.openwebui.com/)
