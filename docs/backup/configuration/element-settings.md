# Element Settings

## Overview

Element settings control the behavior of both the analysis service and Neo4j service. These settings determine:
1. What elements are extracted during analysis
2. How elements are formatted and validated
3. What relationships are created in the database
4. What metadata is captured and stored

## Settings Structure

### Base Element Configuration
```json
{
    "name": "string",                    // Element identifier (e.g., 'emotion', 'topic')
    "enabled": boolean,                  // Whether this element is active
    "description": "string",             // Human-readable description
    "categories": ["string"],            // Valid categories for this element
    "format_template": "string",         // Template for element formatting
    "system_instructions": "string",     // Instructions for AI analysis
    "analysis_instructions": "string",   // Instructions for element extraction
    "requires_topic": boolean,           // Whether topic relationship is required
    "requires_timestamp": boolean,       // Whether timestamp is required
    "additional_fields": ["string"]      // Extra fields to capture
}
```

### Element-Specific Settings

#### Emotion Element
```json
{
    "name": "emotion",
    "enabled": true,
    "categories": ["basic", "complex", "mixed"],
    "format_template": "{name} (intensity: {intensity}) - {context}",
    "system_instructions": "Extract emotions with intensity and context",
    "analysis_instructions": "Identify emotions and their intensity levels",
    "requires_topic": true,
    "requires_timestamp": true,
    "additional_fields": ["intensity", "confidence", "duration"]
}
```

#### Topic Element
```json
{
    "name": "topic",
    "enabled": true,
    "categories": ["personal", "professional", "relationships"],
    "format_template": "{name} - {description}",
    "system_instructions": "Extract main topics discussed",
    "analysis_instructions": "Identify key topics and their descriptions",
    "requires_topic": false,
    "requires_timestamp": true,
    "additional_fields": ["relevance", "frequency"]
}
```

## Analysis Service Integration

### Prompt Generation
1. The analysis service reads element settings from user preferences
2. For each enabled element:
   - System instructions are added to the prompt
   - Format templates are included for output structure
   - Required fields are specified
   - Validation rules are applied

### Example Prompt Construction
```python
def construct_analysis_prompt(settings, transcript):
    enabled_elements = [e for e in settings['analysis_elements'] if e['enabled']]
    
    prompt = f"""
    Analyze the following transcript and extract the following elements:
    
    {format_elements_instructions(enabled_elements)}
    
    Transcript:
    {transcript}
    
    Format the response according to these templates:
    {format_elements_templates(enabled_elements)}
    """
    return prompt
```

## Neo4j Service Integration

### Node Creation
1. For each enabled element:
   - Create corresponding node type
   - Apply element-specific properties
   - Add required metadata
   - Create relationships based on settings

### Relationship Management
1. If `requires_topic` is true:
   - Create topic relationship
   - Add relationship properties
2. If `requires_timestamp` is true:
   - Add timestamp properties
3. Create additional relationships based on element type

### Example Neo4j Query Construction
```cypher
// For enabled emotion element
MATCH (s:Session {id: $session_id})
MERGE (e:Emotion {name: $emotion_name, user_id: $user_id})
ON CREATE SET 
    e.id = $emotion_id,
    e.intensity = $intensity,
    e.confidence = $confidence,
    e.created_at = $timestamp,
    e.updated_at = $timestamp
CREATE (s)-[:HAS_EMOTION {
    context: $context,
    intensity: $intensity,
    confidence: $confidence,
    created_at: $timestamp,
    updated_at: $timestamp
}]->(e)
```

## Validation Rules

### Required Fields
1. Check `requires_topic`:
   - Ensure topic relationship exists
   - Validate topic properties
2. Check `requires_timestamp`:
   - Ensure timestamp fields are present
   - Validate timestamp format
3. Check additional fields:
   - Validate field presence
   - Validate field types
   - Apply field-specific validation

### Element-Specific Validation
1. Emotions:
   - Validate intensity range
   - Check confidence score
   - Ensure context exists
2. Topics:
   - Validate category
   - Check relevance score
   - Ensure description exists

## Error Handling

### Analysis Service
1. Missing required elements:
   - Log warning
   - Skip element if optional
   - Fail if required
2. Invalid format:
   - Attempt to reformat
   - Log error if reformatting fails
3. Missing relationships:
   - Create default relationships
   - Log warning

### Neo4j Service
1. Missing properties:
   - Use default values
   - Log warning
2. Invalid relationships:
   - Skip relationship creation
   - Log error
3. Database errors:
   - Rollback transaction
   - Log error
   - Return error response

## Best Practices

### Settings Management
1. Version control settings
2. Validate settings on update
3. Maintain backward compatibility
4. Document changes

### Performance Considerations
1. Cache frequently used settings
2. Batch element processing
3. Optimize Neo4j queries
4. Use appropriate indexes

### Security
1. Validate all inputs
2. Sanitize element data
3. Check user permissions
4. Log sensitive operations 