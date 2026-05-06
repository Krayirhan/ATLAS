# ATLAS - Project Summary

## What ATLAS Is

ATLAS is a local-first personal AI assistant foundation for Windows. It uses Ollama as the default local LLM runtime and is being aligned to understand text and future voice commands, then safely manage personal PC actions, personal knowledge, routines, and later device/home automation.

## Who It Is For

ATLAS is for a single local user who wants a private, permission-controlled assistant on a Windows PC. The first target is personal control and automation, not team collaboration, enterprise orchestration, or autonomous software development.

## Problem It Solves

ATLAS aims to solve the gap between natural language intent and safe local action:

- understand a user command
- map it to a structured intent
- preview the resulting action
- classify risk
- ask for confirmation when needed
- execute only approved safe actions
- return a clear result
- keep an audit trail

## First Platform

The first platform is Windows. The canonical project root is `E:\ATLAS`. `D:\ATLAS` is not an operational root and writes to `D:` remain outside the ATLAS policy stance.

## First Interaction Model

The first interaction is text. Push-to-talk voice comes later after the action and permission model is documented. Wake word is deferred until privacy and always-listening risks are handled.

## First Action Target

The first action target is PC control:

- open app
- open folder
- show system info
- media play/pause
- volume control
- browser search
- file search preview

## Later Product Layers

Later layers:

- personal preferences and memory
- routine engine
- device registry and room model
- home control adapter
- desktop tray and permission panel
- notification/reminder/calendar assistant
- mobile bridge

## Existing Foundation

The existing CLI, config, safety policy, Ollama provider, context loader, MainAgent, ToolApprovalAgent, SecurityAuditorAgent, MemoryAgent foundation, doctor, audit, and tests are preserved as the core foundation.

Developer-oriented agents remain as parked support tools, not the main product path.
