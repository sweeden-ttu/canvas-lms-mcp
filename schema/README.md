# Schema Files

Schema definitions for Canvas LMS MCP and related data.

## syllabus_schema.json

JSON Schema for **Canvas course and syllabus** data. Use it to:

- Validate or type course/syllabus payloads from the Canvas API
- Document the shape of course objects when `include=syllabus_body` is used on `GET /api/v1/courses/:id`
- Build tools that extract course documents, syllabus body, or module/file references

Canvas syllabus is retrieved with:

```
GET /api/v1/courses/:id?include=syllabus_body
```

The `syllabus_body` field contains HTML. This schema does not define the internal structure of that HTML; it only describes the top-level course object and the presence of `syllabus_body`.

See [verified_canvas_spec.json](../verified_canvas_spec.json) for endpoint verification and sample responses from this project.
