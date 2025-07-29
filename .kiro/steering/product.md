# Product Overview

AI考试生成器 (AI Exam Generator) is an intelligent exam generation system built on the Strands Agent framework. The system generates various types of exam questions based on user-specified parameters including grade level, subject, question types, difficulty, and reference materials.

## Key Features

- **Multi-question types**: Single choice, multiple choice, fill-in-the-blank questions
- **Composite question types**: Automatically distributes question counts across multiple selected types
- **Difficulty levels**: Simple, medium, hard
- **Reference material processing**: Supports URLs and text as reference materials
- **Interactive HTML rendering**: Generated exams can be viewed interactively in browsers
- **Bilingual interface**: Chinese and English support
- **Parallel question generation**: Multiple questions generated simultaneously for efficiency
- **Question caching**: Avoids regenerating similar questions
- **Format auto-repair**: Automatically fixes format issues in generated content

## System Architecture

The system consists of three main components:

1. **Backend Service**: Strands Agent-based service providing exam generation API
2. **Frontend Interface**: React-based user interface for parameter input and result display  
3. **Rendering Service**: Flask-based service converting Markdown exam content to interactive HTML

## Target Users

- Teachers and educators creating exams
- Educational institutions needing automated assessment generation
- Training organizations requiring customized test content