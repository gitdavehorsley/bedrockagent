#!/usr/bin/env python3
"""
AWS Bedrock Agent Configuration Test Script
Tests the CloudFormation template configuration before deployment
"""

import yaml
import json
import boto3
from pathlib import Path

class AgentConfigTester:
    def __init__(self, template_file="bedrock-agent-template.yaml"):
        self.template_file = Path(template_file)
        self.template = None

    def load_template(self):
        """Load and parse the CloudFormation template"""
        try:
            with open(self.template_file, 'r') as f:
                self.template = yaml.safe_load(f)
            print(f"✅ Template loaded successfully: {self.template_file}")
            return True
        except Exception as e:
            print(f"❌ Error loading template: {e}")
            return False

    def validate_template_syntax(self):
        """Validate CloudFormation template syntax"""
        try:
            # Use boto3 to validate template (requires AWS credentials)
            cf_client = boto3.client('cloudformation')
            with open(self.template_file, 'r') as f:
                template_body = f.read()

            cf_client.validate_template(TemplateBody=template_body)
            print("✅ CloudFormation template syntax is valid")
            return True
        except Exception as e:
            print(f"❌ Template validation error: {e}")
            return False

    def check_parameters(self):
        """Check template parameters configuration"""
        if not self.template or 'Parameters' not in self.template:
            print("❌ No Parameters section found in template")
            return False

        parameters = self.template['Parameters']
        required_checks = {
            'AgentName': {'Type': 'String'},
            'FoundationModel': {'Type': 'String'},
            'Environment': {'Type': 'String', 'AllowedValues': ['dev', 'test', 'prod']}
        }

        print("\n🔍 Checking Parameters:")
        for param_name, expected in required_checks.items():
            if param_name not in parameters:
                print(f"❌ Missing parameter: {param_name}")
                continue

            param = parameters[param_name]
            print(f"✅ {param_name}: {param.get('Default', 'No default')}")

            # Check type
            if param.get('Type') != expected['Type']:
                print(f"  ⚠️  Type mismatch: expected {expected['Type']}, got {param.get('Type')}")

            # Check allowed values
            if 'AllowedValues' in expected:
                if 'AllowedValues' not in param:
                    print(f"  ⚠️  Missing AllowedValues for {param_name}")
                elif param['AllowedValues'] != expected['AllowedValues']:
                    print(f"  ⚠️  AllowedValues mismatch for {param_name}")

        return True

    def check_resources(self):
        """Check template resources configuration"""
        if not self.template or 'Resources' not in self.template:
            print("❌ No Resources section found in template")
            return False

        resources = self.template['Resources']
        expected_resources = [
            'BedrockAgentRole',
            'BedrockAgent',
            'BedrockAgentAlias',
            'AgentLogGroup'
        ]

        print("\n🔍 Checking Resources:")
        for resource in expected_resources:
            if resource in resources:
                resource_type = resources[resource].get('Type', 'Unknown')
                print(f"✅ {resource}: {resource_type}")
            else:
                print(f"❌ Missing resource: {resource}")

        return True

    def check_bedrock_agent_config(self):
        """Check Bedrock Agent specific configuration"""
        if not self.template or 'Resources' not in self.template:
            return False

        resources = self.template['Resources']
        if 'BedrockAgent' not in resources:
            print("❌ BedrockAgent resource not found")
            return False

        agent = resources['BedrockAgent']
        properties = agent.get('Properties', {})

        print("\n🔍 Checking Bedrock Agent Configuration:")

        # Check foundation model
        foundation_model = properties.get('FoundationModel', 'Not set')
        print(f"✅ Foundation Model: {foundation_model}")

        # Check if instruction is present
        if 'Instruction' in properties:
            instruction_length = len(properties['Instruction'])
            print(f"✅ Agent Instruction: {instruction_length} characters")
        else:
            print("❌ Missing Agent Instruction")

        # Check idle session TTL
        idle_ttl = properties.get('IdleSessionTTLInSeconds', 'Not set')
        print(f"✅ Idle Session TTL: {idle_ttl} seconds")

        # Check prompt override configuration
        if 'PromptOverrideConfiguration' in properties:
            print("✅ Prompt Override Configuration: Present")
            poc = properties['PromptOverrideConfiguration']
            if 'PromptConfigurations' in poc:
                prompt_count = len(poc['PromptConfigurations'])
                print(f"   📝 {prompt_count} prompt configurations found")
        else:
            print("⚠️  No Prompt Override Configuration")

        return True

    def check_outputs(self):
        """Check template outputs"""
        if not self.template or 'Outputs' not in self.template:
            print("❌ No Outputs section found in template")
            return False

        outputs = self.template['Outputs']
        expected_outputs = [
            'AgentId',
            'AgentAliasId',
            'AgentRoleArn',
            'AgentAliasArn',
            'FoundationModelUsed'
        ]

        print("\n🔍 Checking Outputs:")
        for output in expected_outputs:
            if output in outputs:
                print(f"✅ {output}")
            else:
                print(f"❌ Missing output: {output}")

        return True

    def generate_summary(self):
        """Generate a summary of the template configuration"""
        print("\n📊 Template Summary:")
        print("=" * 50)

        if self.template:
            print(f"Description: {self.template.get('Description', 'No description')}")
            print(f"AWSTemplateFormatVersion: {self.template.get('AWSTemplateFormatVersion', 'Not specified')}")

            if 'Parameters' in self.template:
                print(f"Parameters: {len(self.template['Parameters'])}")
            if 'Resources' in self.template:
                print(f"Resources: {len(self.template['Resources'])}")
            if 'Outputs' in self.template:
                print(f"Outputs: {len(self.template['Outputs'])}")

    def run_all_checks(self):
        """Run all validation checks"""
        print("🚀 Starting AWS Bedrock Agent Template Validation")
        print("=" * 60)

        checks = [
            self.load_template,
            self.check_parameters,
            self.check_resources,
            self.check_bedrock_agent_config,
            self.check_outputs,
        ]

        passed = 0
        for check in checks:
            try:
                if check():
                    passed += 1
            except Exception as e:
                print(f"❌ Error in {check.__name__}: {e}")

        self.generate_summary()

        print(f"\n✅ Validation complete: {passed}/{len(checks)} checks passed")

        if passed == len(checks):
            print("🎉 Template is ready for deployment!")
        else:
            print("⚠️  Please review and fix the issues above")

        return passed == len(checks)

def main():
    tester = AgentConfigTester()
    success = tester.run_all_checks()

    # Try AWS validation if credentials are available
    print("\n🔍 Attempting AWS CloudFormation validation...")
    try:
        tester.validate_template_syntax()
    except Exception as e:
        print(f"⚠️  AWS validation skipped: {e}")
        print("   Make sure you have AWS credentials configured")

if __name__ == "__main__":
    main()
