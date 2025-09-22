# Classroom Behavior Monitoring Agent

This guide shows how to create a classroom behavior monitoring agent using Watsonx Orchestrate.

## Step 1: Access Watsonx Orchestrate Builder

Go to [Watsonx Orchestrate Builder](https://orchestrate.ibm.com)

![Watsonx Orchestrate Homepage](UI/images/watsonx-orchestrate-homepage.png)

## Step 2: Create New Agent

1. Click **"Create New Agent"** button

![Create New Agent Button](UI/images/create-new-agent-button.png)

## Step 3: Configure Agent Settings

1. Choose **"Create from scratch"**
2. Enter agent details:
   - **Agent Name:** `Classroom Behavior Record Agent`
   - **Description:** `An AI agent that helps teachers record and monitor student behavior observations, track behavior patterns, and manage classroom notes efficiently.`

## Step 4: Create Agent

1. Click **"Create"** to proceed with agent creation

![Agent Creation Confirmation](UI/images/agent-creation-confirmation.png)

## Step 5: Add Tools to Agent

1. Navigate to **"Toolset"** section
2. Click **"Add Tool"** button

![Add Tool Button](UI/images/add-tool-button.png)

> **Note:** The AI model displayed may vary based on your configuration. If you have previously imported Gemini, it will show "Gemini 2.5 Flash" instead of the default model.

## Step 6: Import API Tools

1. Click **"Add from file or MCP server"**

![Import Options](UI/images/import-options.png)

2. Select **"Import from file"**

![Import from File Option](UI/images/import-from-file-option.png)

## Step 7: Upload OpenAPI Configuration

1. Upload the `class_notes_openapi.json` file from:
   ```
   WXO-Saint-Gabriel-workshop/LAB_01_CLASSROOM_BEHAVIOR_MONITORING_AGENT/UI/open_api_tools/
   ```

![File Upload Dialog](UI/images/file-upload-dialog.png)

## Step 8: Select Available Tools

Select all the available tools for the classroom behavior monitoring system:

- **View student behavior history**
- **Record student behavior observation** 
- **Send email notification**

![Tool Selection](UI/images/tool-selection.png)

## Step 9: Verify Toolset

The selected tools will now be displayed in the **Toolset** section, ready for use by your agent.

## Step 10: Configure Agent Behavior

1. Navigate to the **"Behavior"** section
2. Add the following instruction to ensure multilingual support:
   ```
   Answer in the same language as user's query.
   ```

![Agent Behavior Configuration](UI/images/agent-behavior-configuration.png)

> **Note:** This instruction ensures your agent responds in the same language (Thai, English, etc.) that the user uses when asking questions.
