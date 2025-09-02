#!/bin/bash

# AWS Bedrock Agent Deployment Script
# This script deploys the Bedrock Agent CloudFormation template

set -e

# Configuration
STACK_NAME="bedrock-agent-test"
TEMPLATE_FILE="bedrock-agent-template.yaml"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}AWS Bedrock Agent Deployment Script${NC}"
echo -e "${YELLOW}=================================${NC}"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

# Check if template file exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}Error: Template file '$TEMPLATE_FILE' not found.${NC}"
    exit 1
fi

echo "Deploying Bedrock Agent to region: $REGION"
echo "Stack name: $STACK_NAME"
echo ""

# Check if stack already exists
if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" &> /dev/null; then
    echo -e "${YELLOW}Stack '$STACK_NAME' already exists. Updating...${NC}"
    OPERATION="update-stack"
else
    echo -e "${GREEN}Creating new stack '$STACK_NAME'...${NC}"
    OPERATION="create-stack"
fi

# Deploy the stack
echo "Deploying CloudFormation stack..."
aws cloudformation $OPERATION \
    --stack-name "$STACK_NAME" \
    --template-body file://$TEMPLATE_FILE \
    --capabilities CAPABILITY_NAMED_IAM \
    --region "$REGION" \
    --parameters \
        ParameterKey=AgentName,ParameterValue=TestAgent \
        ParameterKey=AgentDescription,ParameterValue="Bedrock Agent for OpenWebUI testing with Claude Sonnet 3.7" \
        ParameterKey=FoundationModel,ParameterValue=anthropic.claude-3-5-sonnet-20241022-v2:0 \
        ParameterKey=Environment,ParameterValue=dev

echo ""
echo -e "${GREEN}Waiting for stack deployment to complete...${NC}"

# Wait for stack creation/update to complete
aws cloudformation wait stack-${OPERATION%stack}-complete \
    --stack-name "$STACK_NAME" \
    --region "$REGION"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Stack deployment completed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}Stack Outputs:${NC}"

    # Get and display stack outputs
    aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs' \
        --output table
else
    echo -e "${RED}Stack deployment failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. The agent is now ready for testing with OpenWebUI"
echo "2. You can invoke the agent using the Agent Alias ARN from the outputs above"
echo "3. Check the CloudWatch logs for agent activity"
echo ""
echo -e "${YELLOW}To test the agent manually:${NC}"
echo "aws bedrock-agent-runtime invoke-agent \\"
echo "  --agent-id \$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==\`AgentId\`].OutputValue' --output text) \\"
echo "  --agent-alias-id \$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==\`AgentAliasId\`].OutputValue' --output text) \\"
echo "  --session-id test-session-123 \\"
echo "  --input-text 'Hello, can you help me test this agent?' \\"
echo "  --region $REGION"
