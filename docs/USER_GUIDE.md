# PromptForge User Guide

Welcome to PromptForge! This guide will help you create custom 3D printable models using natural language and AI.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating Your First Model](#creating-your-first-model)
3. [Editing Models](#editing-models)
4. [Adjusting Parameters](#adjusting-parameters)
5. [Print-Readiness Analysis](#print-readiness-analysis)
6. [Exporting Models](#exporting-models)
7. [Tips for Best Results](#tips-for-best-results)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Getting Started

### What is PromptForge?

PromptForge is an AI-powered tool that generates 3D printable models from natural language descriptions. Simply describe what you want to create, and PromptForge will generate parametric CAD code, render a 3D preview, and analyze the model for printability.

### Key Features

- 🤖 **AI-Powered Generation**: Describe your model in plain English
- 💬 **Conversational Editing**: Refine your design through natural conversation
- 🎚️ **Parametric Controls**: Adjust dimensions with intuitive sliders
- 🔍 **Print Analysis**: Automatic detection of printing issues
- 📦 **Multiple Export Formats**: STL, STEP, and GLB support
- 🎨 **Real-time 3D Preview**: See your model instantly

### System Requirements

- Modern web browser (Chrome, Firefox, Safari, or Edge)
- Internet connection
- No software installation required!

---

## Creating Your First Model

### Step 1: Describe Your Model

In the chat panel on the left, type a description of what you want to create. Be specific about:

- **Type of object**: "phone stand", "desk organizer", "planter"
- **Key dimensions**: "50mm wide", "100mm tall"
- **Special features**: "with drainage holes", "angled at 45 degrees"

**Example Prompts:**
```
Create a phone stand that's 80mm wide and angled at 60 degrees

Make a desk organizer with 3 compartments for pens and pencils

Design a small planter pot with drainage holes, 60mm diameter

Create a simple bracket to hold a shelf, 100mm long with mounting holes
```

### Step 2: Review the Generated Model

After a few seconds, you'll see:
- ✅ A 3D preview in the center panel
- 📊 Extracted parameters in the right panel
- 💬 A confirmation message in the chat

### Step 3: Interact with the 3D Viewer

- **Rotate**: Click and drag
- **Zoom**: Scroll wheel or pinch gesture
- **Pan**: Right-click and drag (or Shift + drag)

---

## Editing Models

### Conversational Editing

You can refine your model by continuing the conversation. PromptForge understands context and will modify the existing design.

**Example Conversation:**
```
You: Create a box 50mm on each side
AI: [Generates a 50mm cube]

You: Make it taller, 100mm high
AI: [Updates the box to 50x50x100mm]

You: Add a lid with a hinge
AI: [Adds a hinged lid to the box]

You: Round the corners
AI: [Applies fillets to the edges]
```

### Types of Edits

**Dimension Changes:**
- "Make it wider"
- "Increase the height to 80mm"
- "Make the walls thicker"

**Feature Additions:**
- "Add drainage holes"
- "Include mounting holes"
- "Add a handle on top"

**Feature Modifications:**
- "Make the holes bigger"
- "Change the angle to 45 degrees"
- "Round the edges"

**Feature Removals:**
- "Remove the handle"
- "Take out the center hole"

---

## Adjusting Parameters

### Using Parameter Sliders

After generating a model, you'll see parameter sliders in the right panel. These allow you to adjust dimensions without typing.

**How to Use:**
1. **Drag the slider** to change the value
2. **Type a number** in the input field for precise control
3. **Click "Apply Changes"** to regenerate the model
4. **Click "Reset"** to restore original values

### Parameter Categories

Parameters are organized by type:

- **📏 Dimensions**: Width, height, depth, diameter
- **🏗️ Structure**: Wall thickness, base thickness
- **⚙️ Features**: Hole diameter, spacing, counts
- **📐 Angles**: Rotation, tilt, slope
- **🔢 Counts**: Number of holes, compartments, etc.

### Tips for Parameters

- Start with small adjustments (5-10mm)
- Check the 3D preview after each change
- Use the analysis tool to verify printability
- Reset if you go too far

---

## Print-Readiness Analysis

### Running an Analysis

Click the **"Analyze for 3D Printing"** button in the right panel to check if your model is ready to print.

### Understanding the Report

**Status Indicators:**
- ✅ **Ready to Print**: No critical issues found
- ⚠️ **Needs Attention**: Minor issues that should be addressed
- ❌ **Not Printable**: Critical issues that must be fixed

**Issue Severity:**
- 🔴 **Critical**: Must fix before printing
- 🟡 **Warning**: Should address for best results
- 🔵 **Info**: Optional improvements

### Common Issues

**Thin Walls:**
- **Problem**: Walls thinner than 0.8mm (FDM) or 0.4mm (resin)
- **Solution**: Increase wall thickness parameter or ask AI to "make walls thicker"

**Overhangs:**
- **Problem**: Surfaces angled more than 45° from vertical
- **Solution**: Add supports in your slicer or redesign to reduce overhangs

**Non-Manifold Geometry:**
- **Problem**: Model has holes or self-intersections
- **Solution**: Regenerate the model or ask AI to "fix the geometry"

**Too Large for Print Bed:**
- **Problem**: Model exceeds printer dimensions
- **Solution**: Scale down in your slicer or reduce dimensions

**Trapped Volumes:**
- **Problem**: Enclosed cavities that trap resin or support material
- **Solution**: Add drainage holes or vent holes

### Print Settings Recommendations

The analysis report includes suggested settings:
- **Layer Height**: 0.1-0.3mm depending on detail level
- **Infill**: 15-30% for most functional parts
- **Supports**: When and where to add them
- **Material**: PLA, PETG, or resin recommendations

---

## Exporting Models

### Export Formats

**STL (Stereolithography)**
- Most common format for 3D printing
- Supported by all slicers
- Best for: FDM and resin printing

**STEP (Standard for Exchange of Product Data)**
- Parametric CAD format
- Editable in CAD software
- Best for: Further modification in CAD tools

**GLB (GL Transmission Format)**
- 3D graphics format
- Viewable in web browsers
- Best for: Sharing and visualization

### How to Export

1. **From Chat Panel**: Click the download button next to the model message
2. **From 3D Viewer**: Right-click and select "Export"
3. **Choose Format**: Select STL, STEP, or GLB

### Importing into Slicers

**For FDM Printers (Cura, PrusaSlicer, etc.):**
1. Open your slicer software
2. Import the STL file
3. Position and orient the model
4. Add supports if needed (check analysis report)
5. Slice and save G-code

**For Resin Printers (ChiTuBox, Lychee, etc.):**
1. Open your slicer software
2. Import the STL file
3. Add supports (usually auto-generated)
4. Hollow if needed (for large models)
5. Slice and save to USB

---

## Tips for Best Results

### Writing Effective Prompts

**Be Specific:**
- ❌ "Make a holder"
- ✅ "Create a toothbrush holder with 4 slots, 80mm tall"

**Include Dimensions:**
- ❌ "A big box"
- ✅ "A storage box 150mm x 100mm x 80mm"

**Mention Key Features:**
- ❌ "A planter"
- ✅ "A succulent planter with drainage holes and a saucer"

**Specify Constraints:**
- "Must fit on a 200mm print bed"
- "Walls should be at least 2mm thick"
- "No overhangs greater than 45 degrees"

### Design Considerations

**For FDM Printing:**
- Avoid thin walls (< 0.8mm)
- Minimize overhangs (< 45°)
- Consider print orientation
- Add chamfers instead of sharp corners

**For Resin Printing:**
- Avoid large flat surfaces (suction)
- Include drainage holes for hollow parts
- Minimum wall thickness: 0.4mm
- Consider support removal access

**General Tips:**
- Start simple, add complexity gradually
- Test small versions first
- Use parametric controls for fine-tuning
- Check analysis before printing

### Common Design Patterns

**Functional Parts:**
- Add mounting holes (3-4mm diameter)
- Include clearance for moving parts (0.2-0.5mm)
- Use standard screw sizes (M3, M4, M5)

**Decorative Parts:**
- Add texture or patterns
- Consider multi-material printing
- Use organic shapes and curves

**Containers:**
- Include drainage if needed
- Add grip features (texture, handles)
- Consider stackability

---

## Troubleshooting

### Model Won't Generate

**Possible Causes:**
- Description is too vague or ambiguous
- Requested geometry is impossible
- System is temporarily busy

**Solutions:**
- Be more specific in your description
- Try a simpler design first
- Wait a moment and try again
- Check the error message for hints

### Model Looks Wrong

**Possible Causes:**
- AI misunderstood the description
- Parameters are set incorrectly
- Viewing angle is confusing

**Solutions:**
- Rotate the 3D view to see all angles
- Ask AI to clarify: "Show me from the top"
- Edit with more specific instructions
- Adjust parameters and regenerate

### Export Fails

**Possible Causes:**
- Model has errors (non-manifold)
- File is too large
- Network issue

**Solutions:**
- Run print analysis to check for errors
- Simplify the model
- Try a different export format
- Refresh the page and try again

### Print Fails

**Possible Causes:**
- Model has thin walls or overhangs
- Incorrect slicer settings
- Printer calibration issues

**Solutions:**
- Review the print analysis report
- Add supports in your slicer
- Adjust print orientation
- Calibrate your printer

---

## FAQ

### General Questions

**Q: Do I need to know CAD to use PromptForge?**
A: No! PromptForge is designed for anyone to use, regardless of CAD experience. Just describe what you want in plain English.

**Q: How long does it take to generate a model?**
A: Most models generate in 5-15 seconds, depending on complexity.

**Q: Can I edit the generated code directly?**
A: Currently, editing is done through natural language. Direct code editing may be added in future versions.

**Q: Is there a limit to model complexity?**
A: Models should be reasonably simple (< 1000 faces). Very complex models may take longer or fail to generate.

### Technical Questions

**Q: What CAD system does PromptForge use?**
A: PromptForge uses CadQuery, a Python-based parametric CAD library.

**Q: Can I use the models commercially?**
A: Yes! Models you create are yours to use however you like.

**Q: What AI model powers PromptForge?**
A: PromptForge uses IBM's Granite models via watsonx.ai.

**Q: Can I save my models for later?**
A: Currently, models are session-based. Export your models to save them locally.

### Printing Questions

**Q: Will my model definitely print successfully?**
A: The print analysis helps identify issues, but successful printing also depends on your printer, settings, and material. Always test small versions first.

**Q: What material should I use?**
A: The analysis report suggests materials. PLA is easiest for beginners. PETG is stronger. Resin provides the finest detail.

**Q: Do I need supports?**
A: The analysis report will tell you if supports are needed. Most slicers can auto-generate supports.

**Q: What if my printer is smaller than the model?**
A: Scale down the model in your slicer, or ask PromptForge to generate a smaller version.

---

## Getting Help

### Resources

- **Documentation**: Check the [Developer Guide](DEVELOPER_GUIDE.md) for technical details
- **Examples**: Browse the example library for inspiration
- **Community**: Share your creations and get help from other users

### Reporting Issues

If you encounter a bug or have a feature request:
1. Check if it's a known issue
2. Provide a clear description
3. Include your prompt and any error messages
4. Share screenshots if helpful

---

## What's Next?

Now that you know the basics:

1. **Experiment**: Try creating different types of objects
2. **Iterate**: Refine your designs through conversation
3. **Print**: Export and print your creations
4. **Share**: Show off what you've made!

Happy making! 🎨🖨️✨