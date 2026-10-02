# Changelog

All notable changes to Syntax Sage are documented in this file.

## [1.0.0] - 2026-10-02

### Added

- Single-file source-code analysis
- Whole-project scanning
- Local Python dependency analysis
- Reverse dependency and change-impact tracing
- Project-level question answering
- Verified dependency explanations
- Verified architecture and module-role explanations
- Project pipeline explanations
- AI-assisted code and project reviews
- Deterministic routing for questions that can be answered from verified facts
- Prompt-budget controls
- Project answer cleaning
- Advice validation
- Dependency claim validation
- Single-file review guards
- Project review guards
- AI connection-error handling
- Windows launcher
- Release installation instructions
- Clean `requirements.txt`
- Automated regression test suite

### Accuracy and Safety

- Prevents unsupported dependency claims from being presented as verified facts
- Distinguishes static dependency relationships from confirmed runtime failures
- Excludes the target file itself from change-impact results
- Avoids guessing when import resolution is ambiguous
- Preserves known project errors over conflicting AI-generated claims
- Limits unsupported runtime inference
- Avoids unsolicited code and improvement suggestions unless requested

### Testing

- 230 automated tests passing
- Clean-install test completed successfully
- Fresh virtual-environment dependency installation verified
- Windows launcher verified from a clean project copy
- Manual Option 4 project-question acceptance test completed successfully

### Dependencies

- `ollama==0.6.2`

### Release Status

Syntax Sage v1.0.0 is the first stable release of the core CLI application.
