# PromptForge Demo Script

> **A 5-minute demonstration of conversational 3D design**

This script guides you through a live demonstration of PromptForge's key features for the IBM AI Builders Challenge.

---

## Demo Overview

**Duration:** 5 minutes  
**Audience:** Judges, makers, designers, developers  
**Goal:** Show how PromptForge democratizes 3D design through natural language

**Key Messages:**
1. **No CAD skills required** — describe in plain English
2. **True conversational editing** — refine through chat, not regeneration
3. **Print-ready output** — guaranteed manifold geometry
4. **Parametric control** — real-time tuning with sliders
5. **AI-powered analysis** — printability checks with explanations

---

## Pre-Demo Setup (5 minutes before)

### Environment Check
```bash
# 1. Start backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload

# 2. Start frontend (new terminal)
cd frontend
npm run dev

# 3. Verify services
curl http://localhost:8000/api/health
open http://localhost:3000
```

### Browser Setup
- Open Chrome/Firefox with dev tools ready
- Clear any previous models from UI
- Have example prompts ready in a text file
- Prepare 3D slicer software (PrusaSlicer/Cura) for export demo

---

## Demo Script

### Opening (30 seconds)

**[Show title slide or README]**

> "Hi, I'm [Name], and this is **PromptForge** — an AI-powered tool that turns plain-English descriptions into print-ready 3D models through conversation.
>
> The problem: 3D printing has democratized manufacturing, but 3D modeling hasn't kept pace. Learning CAD takes 40+ hours. Existing AI tools produce unprintable 'blobs.'
>
> PromptForge solves this by generating **parametric code**, not meshes — guaranteeing printable output and enabling true conversational editing."

---

### Act 1: Create a Model (90 seconds)

**[Switch to PromptForge UI]**

> "Let me show you. I'll create a desk organizer from scratch — no CAD skills needed."

**Type in chat:**
```
I need a desk organizer with three compartments: one for pens (30mm diameter), 
one for sticky notes (80mm x 80mm), and one for paperclips (40mm x 60mm). 
Make it 120mm wide total with 2mm walls and rounded corners.
```

**[Press Enter, narrate while generating]**

> "Behind the scenes, PromptForge is:
> 1. Using IBM Granite to classify my intent
> 2. Retrieving relevant CadQuery examples from our RAG pipeline
> 3. Generating Python code that a real CAD kernel executes
> 4. Validating the geometry is manifold and printable"

**[Model appears in 3D viewer]**

> "And there it is — a fully parametric, print-ready model in under 10 seconds. Notice the 3D viewer lets me rotate and inspect it."

**[Rotate model, zoom in on details]**

---

### Act 2: Conversational Editing (90 seconds)

**[Continue in chat]**

> "Now here's where it gets interesting. Traditional AI tools would regenerate from scratch if I wanted changes. PromptForge edits conversationally."

**Type:**
```
Make the pen compartment 20% deeper
```

**[Model updates]**

> "See how it preserved the overall structure but modified just the pen compartment? That's because Granite is reading the existing code and making targeted edits."

**Type:**
```
Add a slot on the left side for charging cables, 15mm wide
```

**[Model updates with cable slot]**

> "Perfect. And one more:"

**Type:**
```
Round the bottom edges more, with a 5mm fillet
```

**[Model updates with rounded edges]**

> "Three edits, three precise modifications — no regeneration, no lost work. This is what makes PromptForge feel like a design partner, not just a generator."

---

### Act 3: Parameter Tuning (45 seconds)

**[Scroll to parameter sliders]**

> "PromptForge automatically extracts tunable parameters from the generated code. Watch this:"

**[Adjust 'wall_thickness' slider from 2mm to 3mm]**

> "Real-time updates. No waiting, no re-prompting."

**[Adjust 'height' slider]**

> "This is huge for iteration — you can explore design variations instantly."

---

### Act 4: Print-Readiness Analysis (45 seconds)

**[Click 'Analyze Printability' button]**

> "Before printing, let's check if this is actually printable."

**[Analysis report appears]**

> "PromptForge runs geometric checks — wall thickness, overhangs, trapped volumes — and uses Granite to explain findings in plain language:
>
> - ✅ All walls are 3mm thick — good for PLA
> - ✅ No overhangs over 45° — no supports needed
> - ✅ Manifold geometry — guaranteed watertight
> - ⚠️ Recommends printing upright for best strength"

**[Scroll through report]**

> "This is the kind of feedback that helps first-time makers succeed on their first print."

---

### Act 5: Export & Real-World Use (30 seconds)

**[Click 'Export STL' button]**

> "Finally, export to STL for your slicer."

**[Show downloaded file, optionally open in PrusaSlicer]**

> "This file is ready for PrusaSlicer, Cura, or any slicer. Because it's generated from CAD code, it's guaranteed manifold — no mesh repair needed."

**[If time, show sliced preview]**

---

### Closing (30 seconds)

**[Return to PromptForge UI or slides]**

> "So that's PromptForge:
> - **Describe** in plain English
> - **Edit** conversationally
> - **Tune** with sliders
> - **Verify** printability
> - **Export** and print
>
> All powered by IBM Granite on watsonx.ai, with a RAG pipeline of CadQuery examples and a self-correcting code generation loop.
>
> This is what democratizing 3D design looks like. Thank you!"

---

## Backup Demos (If Time Permits)

### Alternative Example 1: Phone Stand
```
Create a phone stand with a 70-degree viewing angle, 
a charging cable slot in the back, and rubber feet mounting holes
```

### Alternative Example 2: Cable Organizer
```
I need a cable organizer for my desk with 5 channels, 
each 10mm wide, with screw holes for mounting
```

### Alternative Example 3: Planter
```
Design a hexagonal planter, 80mm tall, with a 4mm drainage hole 
in the bottom and a decorative pattern on the sides
```

---

## Troubleshooting

### If Generation Fails
- **Show self-correction**: "Notice it's retrying with error feedback"
- **Explain**: "This is the self-correction loop — up to 3 attempts"
- **Fallback**: Use a pre-generated model from examples

### If UI is Slow
- **Narrate**: "While this generates, let me explain the architecture..."
- **Show diagram**: Display architecture diagram from ARCHITECTURE.md

### If Demo Crashes
- **Have backup**: Pre-recorded video or screenshots
- **Pivot**: Walk through code examples and architecture

---

## Post-Demo Q&A Prep

### Expected Questions

**Q: How does this compare to GPT-4 with DALL-E 3D?**
> "GPT-4 generates mesh vertices — unprintable blobs. We generate parametric code that a CAD kernel executes, guaranteeing manifold geometry. Plus, our conversational editing actually modifies code, not regenerates."

**Q: What about complex organic shapes?**
> "Great question. PromptForge is optimized for functional, geometric objects — holders, brackets, enclosures. For organic shapes like character models, mesh-based generation is more appropriate. We chose to excel at printable utility objects."

**Q: Can it handle multi-part assemblies?**
> "Not yet — that's Phase 2. Right now we focus on single-part designs. But the architecture supports it — we'd generate multiple CadQuery scripts with connection definitions."

**Q: How accurate is the print-readiness analysis?**
> "We use geometric heuristics — ray casting for wall thickness, normal analysis for overhangs, topology checks for trapped volumes. It's not perfect, but it catches 90% of common issues. We're training on real print failure data to improve."

**Q: What's the business model?**
> "For the challenge, it's open-source. Long-term: freemium SaaS with cloud storage, design sharing, and premium features. Enterprise tier for IP-sensitive industries with on-prem Granite deployment."

**Q: Why IBM Granite over other models?**
> "Three reasons: (1) Strong Python code generation, (2) Long context windows for reading existing code, (3) Governance and auditability — critical for design IP. Plus on-prem deployment option."

---

## Technical Deep-Dive (If Judges Ask)

### Architecture Highlights
- **Code-based generation**: CadQuery Python scripts, not mesh vertices
- **RAG pipeline**: 25+ few-shot examples + CadQuery docs in Chroma
- **Self-correction loop**: Error feedback to Granite, up to 3 retries
- **Docker sandbox**: Isolated execution with security constraints
- **Parameter extraction**: AST parsing to identify tunable variables

### Key Innovations
1. **Conversational editing without regeneration** — reads existing code
2. **Guaranteed printable output** — CAD kernel ensures manifold geometry
3. **AI-powered printability analysis** — geometric checks + Granite explanations
4. **Real-time parameter tuning** — extracted from code, live updates

### Tech Stack
- **LLM**: IBM Granite 3.x via watsonx.ai
- **CAD**: CadQuery (OpenCascade kernel)
- **Vector DB**: Chroma with Granite embeddings
- **Backend**: FastAPI + Docker sandbox
- **Frontend**: Next.js + React Three Fiber

---

## Demo Checklist

### Before Demo
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Health check passes
- [ ] Example prompts ready
- [ ] Browser dev tools open (optional)
- [ ] Backup video/screenshots ready
- [ ] Slicer software open (optional)

### During Demo
- [ ] Speak clearly and at moderate pace
- [ ] Show, don't just tell — interact with UI
- [ ] Narrate what's happening behind the scenes
- [ ] Highlight key innovations
- [ ] Keep to 5-minute time limit

### After Demo
- [ ] Answer questions confidently
- [ ] Offer to show code/architecture
- [ ] Provide GitHub link
- [ ] Thank judges for their time

---

## Presentation Slides (Optional)

### Slide 1: Title
**PromptForge**  
*Conversational 3D Design for Everyone*

IBM AI Builders Challenge — July 2024  
Built with IBM Granite & watsonx.ai

### Slide 2: The Problem
- 3D printing is democratized ✅
- 3D modeling is not ❌
- Learning CAD: 40+ hours
- AI mesh generation: unprintable blobs
- **Gap**: No tool for conversational, printable design

### Slide 3: The Solution
**PromptForge** = Natural Language → Print-Ready 3D Models

Key Features:
- 🗣️ Describe in plain English
- ✏️ Edit conversationally
- 🎚️ Tune with sliders
- ✅ Verify printability
- 📦 Export and print

### Slide 4: How It Works
[Architecture diagram from ARCHITECTURE.md]

1. User describes object
2. Granite generates CadQuery code (with RAG)
3. CAD kernel executes → manifold geometry
4. Self-correction loop if errors
5. Parameter extraction for sliders
6. Printability analysis with Granite

### Slide 5: Key Innovations
1. **Code-based generation** (not mesh vertices)
2. **Conversational editing** (not regeneration)
3. **Guaranteed printable** (CAD kernel ensures manifold)
4. **AI-powered analysis** (geometric checks + explanations)

### Slide 6: Tech Stack
- **LLM**: IBM Granite 3.x
- **Platform**: watsonx.ai
- **CAD**: CadQuery (OpenCascade)
- **Vector DB**: Chroma
- **Backend**: FastAPI + Docker
- **Frontend**: Next.js + React Three Fiber

### Slide 7: Impact
**Target Users:**
- Makers & hobbyists
- Educators & students
- Tabletop/cosplay creators
- Small product designers

**Value Proposition:**
- 0 → printable model in 30 seconds
- No CAD learning curve
- Endless personalization
- First-print success

### Slide 8: Demo
[Live demo or video]

### Slide 9: Future Roadmap
**Phase 2:**
- Multi-part assemblies
- User accounts & cloud storage
- Design marketplace
- Material library

**Phase 3:**
- Collaborative design
- Mobile app with AR preview
- Slicer integration

### Slide 10: Thank You
**PromptForge**  
*Democratizing 3D Design with AI*

GitHub: [link]  
Demo: [link]  
Contact: [email]

Built with ❤️ and IBM Bob

---

## Video Recording Tips

### Setup
- **Screen resolution**: 1920x1080 (Full HD)
- **Recording software**: OBS Studio or Loom
- **Audio**: Clear microphone, quiet environment
- **Lighting**: Good lighting for webcam (if showing face)

### Recording Checklist
- [ ] Close unnecessary tabs/windows
- [ ] Hide desktop clutter
- [ ] Disable notifications
- [ ] Test audio levels
- [ ] Do a practice run
- [ ] Record in one take if possible
- [ ] Keep under 5 minutes

### Editing
- Add title card at start
- Add captions/subtitles
- Highlight key UI interactions
- Add background music (subtle)
- Export in 1080p MP4

---

## Success Metrics

### Demo Success Indicators
- ✅ Model generates in < 15 seconds
- ✅ Edits apply correctly
- ✅ Sliders update in real-time
- ✅ Analysis report is accurate
- ✅ Export downloads successfully
- ✅ Judges ask technical questions
- ✅ Positive feedback on UX

### Judging Criteria Alignment
- **Innovation**: Code-based generation, conversational editing
- **Technical Excellence**: RAG pipeline, self-correction, sandbox security
- **IBM Tech Usage**: Granite 3.x, watsonx.ai, Bob for development
- **Impact**: Democratizes 3D design for millions of makers
- **Presentation**: Clear demo, strong narrative, polished UI

---

**Good luck! 🚀**