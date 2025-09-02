# AWS Bedrock Agent Deployment Troubleshooting Guide

## Issue: "AmazonBedrockFullAccess policy does not exist"

### Problem Description
You're encountering an error stating that the `AmazonBedrockFullAccess` policy doesn't exist or isn't attachable.

### Root Causes and Solutions

#### 1. **Using Old Template Version**
**Symptoms**: Error persists even after template updates
**Solution**:
- Ensure you're using the latest version from GitHub
- Pull the latest changes: `git pull origin main`
- Verify no local cached versions exist

#### 2. **CloudFormation Template Caching**
**Symptoms**: AWS Console or CLI still references old policy
**Solution**:
- **CloudFormation Console**: Refresh the page and try redeploying
- **CLI**: Use `aws cloudformation validate-template` to verify template syntax
- **Cache Clearing**: Wait 5-10 minutes and retry deployment

#### 3. **Regional Availability**
**Symptoms**: Policy works in one region but not another
**Solution**:
- Some managed policies may not be available in all AWS regions
- Check your deployment region: `us-east-1`, `us-west-2`, `eu-west-1`, etc.
- Consider using inline policies (which is what the current template uses)

#### 4. **AWS Account Permissions**
**Symptoms**: Policy creation/modification fails
**Solution**:
- Ensure your AWS account has permissions to create IAM policies
- Check if your account is part of an AWS Organization with SCPs
- Verify you're not using a sandbox/demo account with restricted permissions

### Current Template Status ✅

The latest template (`bedrock-agent-template.yaml`) **does NOT use** the problematic `AmazonBedrockFullAccess` managed policy. Instead, it uses:

#### Inline Policy with Comprehensive Permissions:
```yaml
Policies:
  - PolicyName: BedrockAgentPolicy
    PolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Action:
            - bedrock:InvokeModel
            - bedrock:InvokeModelWithResponseStream
          Resource:
            - !Sub 'arn:aws:bedrock:*::foundation-model/${FoundationModel}'
        - Effect: Allow
          Action:
            - bedrock:ListFoundationModels
            - bedrock:GetFoundationModel
            - bedrock:CreateAgent
            - bedrock:UpdateAgent
            - bedrock:DeleteAgent
            - bedrock:GetAgent
            - bedrock:ListAgents
            - bedrock:CreateAgentAlias
            - bedrock:UpdateAgentAlias
            - bedrock:DeleteAgentAlias
            - bedrock:GetAgentAlias
            - bedrock:ListAgentAliases
            - bedrock:InvokeAgent
          Resource: '*'
        - Effect: Allow
          Action:
            - logs:CreateLogGroup
            - logs:CreateLogStream
            - logs:PutLogEvents
            - logs:DescribeLogGroups
            - logs:DescribeLogStreams
          Resource: !Sub 'arn:aws:logs:*:*:log-group:/aws/bedrock/*'
```

### Verification Steps

#### 1. Check Template Version
```bash
git log --oneline -5
# Look for commit: "Add comprehensive Bedrock agent permissions"
```

#### 2. Validate Template
```bash
aws cloudformation validate-template --template-body file://bedrock-agent-template.yaml
```

#### 3. Check for Policy References
```bash
grep -n "AmazonBedrockFullAccess" bedrock-agent-template.yaml
# Should return no results
```

### Alternative Deployment Methods

#### Option 1: Use AWS Console
1. Go to CloudFormation in AWS Console
2. Upload `bedrock-agent-template.yaml`
3. Configure parameters
4. Deploy stack

#### Option 2: Use CLI with Explicit Region
```bash
aws cloudformation create-stack \
  --stack-name bedrock-agent-test \
  --template-body file://bedrock-agent-template.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

#### Option 3: Deploy from GitHub URL
```bash
aws cloudformation create-stack \
  --stack-name bedrock-agent-test \
  --template-url https://raw.githubusercontent.com/gitdavehorsley/bedrockagent/main/bedrock-agent-template.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### Foundation Model Availability

Ensure the Claude Sonnet 3.7 model is available in your region:
- **Model ID**: `anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Available Regions**: us-east-1, us-west-2, eu-west-1, ap-southeast-1, ap-northeast-1

### Additional Debugging

#### Check AWS CLI Configuration
```bash
aws configure list
aws sts get-caller-identity
```

#### Check Bedrock Model Access
```bash
aws bedrock list-foundation-models --region us-east-1
```

#### Check CloudWatch Logs (after deployment)
```bash
aws logs describe-log-groups --log-group-name-prefix /aws/bedrock/
```

### If Issues Persist

1. **Check AWS Service Health Dashboard**
2. **Verify Account Limits and Quotas**
3. **Contact AWS Support** with specific error messages
4. **Try Different Region** where Bedrock services are available

### Success Indicators

✅ **Successful Deployment Signs:**
- CloudFormation stack shows `CREATE_COMPLETE`
- IAM role created successfully
- Bedrock agent appears in AWS Console
- No policy-related errors in CloudWatch logs

### Quick Fix Commands

```bash
# Ensure latest version
git pull origin main

# Validate template
python test-agent-config.py

# Deploy with explicit parameters
aws cloudformation create-stack \
  --stack-name bedrock-agent-test \
  --template-body file://bedrock-agent-template.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters ParameterKey=AgentName,ParameterValue=TestAgent \
               ParameterKey=FoundationModel,ParameterValue=anthropic.claude-3-5-sonnet-20241022-v2:0 \
               ParameterKey=Environment,ParameterValue=dev \
  --region us-east-1
```

## Issue: "Invalid JSON in the prompt" for BasePromptTemplate

### Problem Description
CloudFormation validation fails with "Invalid JSON in the prompt" for PRE_PROCESSING and ORCHESTRATION prompt types.

### Root Cause
AWS Bedrock expects prompt templates to be in a specific JSON format that matches the Anthropic Claude API structure, not plain text.

### Solution ✅
**Fixed in latest template version** - The prompt templates now use the correct JSON structure:

#### Correct JSON Format Structure:
```json
{
  "anthropic_version": "bedrock-2023-05-31",
  "max_tokens": 1000,
  "system": "System instructions here",
  "messages": [
    {
      "role": "user",
      "content": "User message with {{.template_variables}}"
    }
  ]
}
```

#### Key Changes Made:
1. **Added `anthropic_version`** field for Claude compatibility
2. **Structured as proper JSON** with `system` and `messages` fields
3. **Template variables** properly placed in message content
4. **Removed plain text formatting** that caused validation errors

#### Verification:
```bash
# Check latest commit includes the fix
git log --oneline | head -3

# Validate template syntax
aws cloudformation validate-template --template-body file://bedrock-agent-template.yaml
```

### Contact and Support

If you're still experiencing issues:
1. Check the GitHub repository for updates
2. Provide specific error messages and region information
3. Verify your AWS account permissions and quotas
4. Ensure you're using the latest template version (commit `789d566`)
