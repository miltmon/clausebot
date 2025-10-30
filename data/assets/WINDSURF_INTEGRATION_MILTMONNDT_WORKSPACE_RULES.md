# MiltmonNDT Workspace File Structure & Organizational Rules
## For Windsurf Integration & Collaboration

**Version**: 1.0.0
**Last Updated**: August 28, 2025, 5:30 PM PDT
**Purpose**: Enable Windsurf to understand and maintain MiltmonNDT workspace structure and rules

---

## 🏗️ **WORKSPACE ARCHITECTURE OVERVIEW**

The MiltmonNDT workspace (`C:\Users\miltm\MiltmonNDT_Workspace`) is organized around the **ClauseBot ecosystem** with strict file structure rules to maintain compatibility across multiple AI agents (Cursor, Windsurf, Gemini, Grok, Copilot).

### **Core Principle**:
**"Every file has a purpose, every purpose has a place."**

---

## 📁 **PRIMARY DIRECTORY STRUCTURE**

### **Root Level (`MiltmonNDT_Workspace/`)**
```
├── clausebot_core/              # Core ClauseBot API & database
├── Deployment Folder/           # Docker containers & production configs
├── docs/                        # Documentation & brand architecture
├── morphic-ai-answer-engine-generative-ui-main/  # Morphic AI integration
├── [tracking files]             # Status reports, bulletins, schemas
├── [content assets]             # PDFs, HTMLs, CSVs, images
└── [integration configs]        # API contracts, Postman collections
```

### **Key Architecture Components**

#### **1. `clausebot_core/` - Technical Foundation**
- **Purpose**: Core ClauseBot API, database models, configuration
- **Owner**: Cursor (primary), Windsurf (secondary)
- **Rules**:
  - ✅ All Python files must include proper docstrings
  - ✅ Environment variables stored in `env_template.txt` (never commit actual `.env`)
  - ✅ Database migrations tracked in `models.py`
  - ✅ API endpoints documented in `clausebot_readme.md`

#### **2. `Deployment Folder/` - Production Environment**
- **Purpose**: Docker Compose, containers, production deployment
- **Owner**: DevOps (Cursor/Windsurf shared)
- **Rules**:
  - ✅ Never modify `docker-compose.yml` without testing locally first
  - ✅ All environment configs must have `.example` templates
  - ✅ Container logs stored in `/logs` subdirectory

#### **3. `docs/` - Documentation Hub**
- **Purpose**: Brand architecture, content delivery, strategic documentation
- **Owner**: Content team (Windsurf primary for content, Cursor for technical)
- **Rules**:
  - ✅ All `.md` files must follow consistent header structure
  - ✅ Brand documents prefixed with `CLAUSEBOT_` or `MILTMONNDT_`
  - ✅ Strategic documents include date stamps in filename

---

## 🔄 **CLOUD STORAGE INTEGRATION RULES**

### **Dropbox Integration**
- **Path**: `C:\Users\miltm\Dropbox\`
- **Purpose**: **ARCHIVE & SOURCE MATERIAL ONLY**
- **Rules**:
  - ⚠️ **NEVER modify Dropbox files directly from workspace**
  - ✅ Copy Dropbox content to workspace for processing
  - ✅ Dropbox serves as "single source of truth" for source materials
  - ✅ Content flows: `Dropbox → Workspace → Git → Production`

### **Google Drive Integration**
- **Purpose**: **COLLABORATION & EXTERNAL SHARING**
- **Rules**:
  - ✅ Use for sharing with external stakeholders
  - ✅ Export/import to workspace for processing
  - ⚠️ Never use as primary storage for development files

### **Local Workspace Priority**
- **Rule**: Workspace is the **active development environment**
- **Backup Flow**: `Workspace → Git → Cloud Backup`
- **Recovery Flow**: `Git → Workspace` (never direct from cloud storage)

---

## 📋 **FILE NAMING CONVENTIONS**

### **Status & Tracking Files**
```
[PROJECT]_[TYPE]_[DATE].md
Examples:
- DEPLOYMENT_STATUS_FINAL_20250828.md
- VICTORY_BULLETIN_ADDENDUM_20250828.md
- Operational_Coordination_Report_20250828.md
```

### **Configuration Files**
```
[system]_[purpose]_[version].ext
Examples:
- clausebot_config.py
- supabase_bubble_tables_schema.sql
- fabtech_form_crm_schema_20250825.csv
```

### **Integration Assets**
```
[source]_[target]_[purpose].ext
Examples:
- Bubble_ClauseBot_API_Contract_v1.md
- ClauseBot_Bubble_Postman_README.md
- clausebot_smoke_test_simple.ps1
```

---

## 🚫 **CRITICAL RULES & RESTRICTIONS**

### **Emoji Protocol** [[memory:3742558]]
- ✅ **ALLOWED**: `.md files`, log summaries with UTF-8 output, visual/UI assets
- ❌ **FORBIDDEN**: `.ps1/.csv scripts`, CLI outputs, file/folder names
- **Settings**: `emoji_safe_mode=true`, `utf8_force=true`, `output_encoding=UTF8`

### **File Modification Rules**
1. **Database Files**: Only modify through proper migration scripts
2. **Docker Configs**: Test locally before committing
3. **API Contracts**: Version control all changes (`v1`, `v2`, etc.)
4. **Environment Files**: Never commit actual API keys (use templates)

### **Cross-Agent Coordination**
- **File Locks**: Use git branch strategy for concurrent work
- **Status Updates**: Log all major changes in daily status files
- **Communication**: Use standardized commit messages and PR descriptions

---

## 🎯 **PROJECT-SPECIFIC RULES**

### **ClauseBot Development**
- **Database**: PostgreSQL with pgvector extension
- **API**: FastAPI with OpenAPI documentation
- **Testing**: Postman collections for API validation
- **Deployment**: Docker Compose for local development

### **Content Management**
- **Standards Data**: Load through `load_sample_standards_data.py`
- **Compliance Matrix**: Tracked in Airtable with SHA256 evidence hashes
- **Track System**: Defined in `track_program_system_map.md`

### **Integration Points**
- **Bubble Dashboard**: CORS configured for `miltmon-80193.bubbleapps.io`
- **Supabase**: Schema defined in `supabase_bubble_tables_schema.sql`
- **Morphic AI**: Answer engine integration in dedicated directory

---

## ⚡ **WINDSURF-SPECIFIC GUIDELINES**

### **When Working in This Workspace**
1. **Check Existing Status**: Always read latest `*_STATUS_*.md` files first
2. **Respect File Ownership**:
   - Cursor: Technical/API development
   - Windsurf: Content/documentation/integration
3. **Update Status Files**: Log your changes in appropriate status documents
4. **Test Locally**: Use `clausebot_smoke_test.ps1` before committing changes

### **Collaboration Protocol**
- **Before Major Changes**: Check with Cursor via status files
- **API Modifications**: Update both code and documentation
- **Content Updates**: Maintain consistency with brand architecture
- **Testing**: Run compliance matrix validation after changes

### **File Access Priorities**
- **High Priority**: `docs/`, content files, integration configs
- **Medium Priority**: Database schemas, API contracts
- **Low Priority**: Core ClauseBot engine files (Cursor's domain)

---

## 📊 **CURRENT PROJECT STATUS** (As of August 28, 2025)

### **Phase 5: Compliance Matrix Automation** (92% Complete)
- ✅ 8/10 compliance claims verified and automated
- ✅ Postman collection operational
- ✅ Airtable integration with SHA256 evidence hashing
- ⚠️ ANSI Z49.1 content gap identified
- ⚠️ GA4 analytics configuration pending

### **FABTECH 2025 Readiness** (<70 days)
- ✅ Core demo functionality verified
- ✅ Bubble dashboard integration complete
- ✅ Compliance evidence trail established
- 🎯 Target: 8-minute live demo with investor handout

### **Immediate Priorities**
1. Content gap analysis and filling
2. Final compliance matrix validation
3. FABTECH demo script refinement
4. Victory Bulletin finalization

---

## 🔧 **DEVELOPMENT ENVIRONMENT SETUP**

### **Required Tools**
- **Git**: Version control and collaboration
- **Docker**: Local development environment
- **Node.js/npm**: Frontend development
- **Python 3.9+**: Backend development
- **PostgreSQL**: Database (via Docker)

### **Environment Variables**
Copy `clausebot_core/env_template.txt` to `.env` and configure:
- `OPENAI_API_KEY`
- `CLAUDE_API_KEY`
- `AIRTABLE_API_KEY`
- `DATABASE_URL`

### **Testing & Validation**
- **API Testing**: Use Postman collections in workspace
- **Smoke Tests**: Run `clausebot_smoke_test.ps1`
- **Compliance**: Check Airtable matrix for verified claims

---

## 📞 **EMERGENCY PROTOCOLS**

### **If Something Breaks**
1. **Check Status Files**: Latest deployment and operational reports
2. **Run Smoke Tests**: `clausebot_smoke_test_simple.ps1`
3. **Check Docker Health**: `docker compose ps` in Deployment Folder
4. **Restore from Git**: Known-good state recovery

### **Cross-Agent Communication**
- **Status Updates**: Use standardized status file format
- **Critical Issues**: Flag in commit messages with `[URGENT]`
- **Coordination**: Reference relevant files and line numbers

---

## 🎯 **SUCCESS METRICS**

### **File Organization**
- ✅ No orphaned files (every file has clear purpose)
- ✅ Consistent naming conventions
- ✅ Proper version control
- ✅ Clean separation of concerns

### **Collaboration Efficiency**
- ✅ Minimal file conflicts between agents
- ✅ Clear ownership and responsibility
- ✅ Rapid issue resolution
- ✅ Maintained project momentum

**Remember**: This workspace serves the **ClauseBot ecosystem** and **FABTECH 2025 preparation**. Every action should support these strategic objectives while maintaining the file structure integrity that enables multi-agent collaboration.

---

**For questions or clarifications, reference the latest status files or check the `docs/` directory for detailed project documentation.**
