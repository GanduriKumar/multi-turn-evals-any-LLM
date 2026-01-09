# Coverage Generator - Beginner's Guide

## What Is This Tool?

Imagine you're testing a customer service chatbot. You want to make sure it handles **lots of different situations** correctly. The Coverage Generator helps you create a diverse set of test conversations automatically, so you don't have to write thousands of tests by hand.

Think of it like a **recipe generator** that creates balanced meal plans—it ensures you get the right mix of proteins, carbs, and veggies. Similarly, this tool ensures you get the right mix of:
- **Easy, medium, and hard** test cases
- **Different topics** (refunds, payments, shipping, etc.)
- **Different customer types** (price-sensitive, brand-loyal, etc.)

---

## 🚀 Step-by-Step Guide

### **1. Start the Application**

First, you need to run two programs:

**Backend (the engine):**
```powershell
# In VS Code terminal
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

**Frontend (the webpage):**
```powershell
# In a new terminal
cd frontend
npm run dev
```

Then open your browser to: `http://localhost:5173`

---

### **2. Navigate to Coverage Generator**

Click **"Coverage Generator"** in the navigation menu (left sidebar or top menu).

You'll see two main sections:

---

## 📊 **Section 1: Coverage Strategy (Server)**

This controls **HOW** the datasets are generated. Think of it as the "recipe settings."

| Setting | What It Means | Recommended Value |
|---------|---------------|-------------------|
| **Mode** | How to mix scenarios | **pairwise** (faster, smart mixing) |
| **t** | Coverage depth | **2** (ensures good variety) |
| **Budget** | Max scenarios per topic | **120** (enough for thorough testing) |
| **Seed** | Random number starter | **42** (keeps results consistent) |
| **Per-behavior** | Scenarios per topic | **100** (balanced set size) |
| **Min/domain** | Minimum per category | **3** (ensures all categories covered) |

### Simple Explanation:
- **Per-behavior = 100**: For each topic (like "Refunds"), generate 100 test cases
- **Min/domain = 3**: Make sure every category (Orders, Payments, etc.) gets at least 3 tests
- **Seed = 42**: Using the same seed always gives you the same tests (useful for consistency)

**What to do:** Leave defaults, or adjust **Per-behavior** if you want more/fewer tests. Click **Save** when done.

---

## 📝 **Section 2: Coverage Generator**

This is where you actually **create** the datasets.

### **Step 2.1: Select What to Test (Optional)**

You'll see two dropdown boxes:

**Domains** (Categories):
- Orders & Returns
- Payments & Refunds/Chargebacks
- Promotions & Pricing
- Shipping & Logistics
- Account & Security
- Restricted Items & Compliance
- Marketplace Policy/Disputes
- Inventory & Availability

**Behaviors** (Specific Actions):
- Refund/Exchange/Cancellation
- Price match/Discount/Coupon stacking
- Post-purchase modifications
- Availability workarounds
- Restricted items or cross-border compliance
- PII access/deletion
- Chargeback disputes
- Adversarial/trap attempts

**What to do:**
- **Leave both empty** to generate tests for **everything** (recommended first time)
- **OR** hold Ctrl and click specific ones to test only those areas

---

### **Step 2.2: Choose Options**

Three checkboxes:

| Checkbox | What It Does | When to Use |
|----------|--------------|-------------|
| **Combined (per-domain + global)** | Groups tests by category + one big file | ✅ **Always check** (easier to use) |
| **Save to server** | Stores files on your computer | ✅ **Check** when ready to save |
| **Overwrite** | Replaces old files if they exist | ⚠️ **Check** only if updating existing tests |

**What to do:** 
1. Check **Combined**
2. Don't check **Save** yet (we'll preview first)

---

### **Step 2.3: Preview Your Tests**

Click the **"Preview coverage"** button.

You'll see a table showing:
- **domain**: Category name
- **behavior**: Action being tested  
- **raw_total**: Total possible tests
- **final_total**: Tests that will be generated (after removing duplicates/extremes)

**Example:**
```
domain: Orders & Returns
behavior: Refund/Exchange/Cancellation
raw_total: 432
final_total: 100
```

This means: "For refunds in orders, there are 432 possible scenarios, but we smartly picked 100 diverse ones."

---

### **Step 2.4: Generate Tests (Dry Run)**

Without checking **Save**, click **"Generate"**.

You'll see a message like:
> "Generated 64 dataset(s) (dry run)"

This shows how many test files would be created, but **nothing is saved yet**. It's a safe preview.

---

### **Step 2.5: Save for Real**

When you're happy:
1. ✅ Check **"Save to server"**
2. Click **"Generate"** again

You'll see:
> "Saved 64 dataset(s) to server"

**Where are the files?** 
- In your project folder: `datasets/commerce/`
- Files are named like: `coverage-orders-returns-combined-1.0.0.dataset.json`
- Each dataset has a matching `.golden.json` file with expected answers

**Path structure:**
- **Flat mode** (default): All files in `datasets/commerce/`
- **Hierarchical mode**: Organized as `datasets/commerce/<behavior>/<version>/`

You can change the mode in the **Coverage Strategy** section.

---

## 🎯 **Quick Workflow (5 Minutes)**

1. **Adjust settings** (optional): Change "Per-behavior" to 50 if you want fewer tests
2. **Click "Save"** in Strategy section
3. **Leave dropdowns empty** (test everything)
4. **Check "Combined"**
5. **Click "Preview coverage"** → Review the table
6. **Click "Generate"** → See dry run message
7. **Check "Save to server"** + **Click "Generate"** → Files saved!
8. **Download reports**: Click "Download Summary CSV" to see a spreadsheet

---

## 📥 **Understanding Your Generated Tests**

Each test file contains:
- **U1**: First customer message ("I need a refund for order #12345")
- **U2**: Follow-up message ("Actually, can I get store credit instead?")
- **Expected answer**: What the chatbot should say

**Example scenario:**
```json
{
  "domain": "Orders & Returns",
  "behavior": "Refund/Exchange/Cancellation", 
  "messages": {
    "u1": "I need help with my recent order. I'm high on price...",
    "u2": "Actually, the item is unavailable now. Can we substitute?"
  },
  "expected": {
    "outcome": "Allowed",
    "a2_canonical": "I will verify your order and, per policy, process a refund..."
  }
}
```

---

## 🔍 **What Makes This "Optimized"?**

The tool ensures:
1. **Balanced difficulty**: ~50% hard, ~35% medium, ~15% easy scenarios
2. **Good coverage**: Tests all important combinations (price-sensitive + out-of-stock, brand-loyal + refund, etc.)
3. **No duplicates**: Removes redundant tests
4. **Minimum variety**: Every category gets at least 3 tests (not all in one area)

**Analogy**: Like a well-balanced exam that tests Chapter 1, Chapter 2, and Chapter 3 equally, with easy/medium/hard questions for each chapter.

---

## ❓ **Common Questions**

**Q: How long does generation take?**  
A: 5-30 seconds for 800 tests (all domains/behaviors).

**Q: Can I regenerate with different tests?**  
A: Yes! Change the **Seed** number (e.g., 42 → 99) to get different random selections.

**Q: What if I only want to test refunds?**  
A: In "Behaviors" dropdown, select only "Refund/Exchange/Cancellation", then click Generate.

**Q: Can I delete generated files?**  
A: Yes, just delete folders in `datasets/commerce/`.

**Q: What's the difference between "Mode: pairwise" and "Mode: exhaustive"?**  
A: 
- **Pairwise**: Smart mixing—tests all important 2-way combinations (faster, 100 tests per topic)
- **Exhaustive**: Tests every possible combination (slower, thousands of tests)
- **Recommendation**: Use pairwise unless you need complete coverage

**Q: Why do I need to set a seed?**  
A: The seed controls randomization. Same seed = same tests every time. This is useful when:
- Sharing results with teammates (everyone gets identical tests)
- Reproducing bugs (re-run the exact same scenarios)
- Comparing different chatbot versions fairly

---

## 🔧 **Advanced: Regenerating Existing Datasets**

If you already have datasets and want to update them with optimized coverage:

1. Scroll to **"Regenerate Optimized"** section (bottom of page)
2. Enter existing dataset ID (e.g., `coverage-orders-returns-combined-1.0.0`)
3. Click **"Regenerate"**
4. Files will be overwritten with new optimized scenarios

**When to use**: After changing strategy settings (e.g., increasing Per-behavior from 100 → 150).

---

## ✅ **You're Done!**

You now have optimized test datasets ready to evaluate chatbots. 

**Next steps:**
- Use the **"Runs"** page to test a chatbot against these scenarios
- Use the **"Datasets"** page to browse/edit individual test cases
- Check the **"Reports"** page to analyze test results

---

## 📚 **Related Documentation**

- [User Guide](../UserGuide.md) - Full application overview
- [Multi-Turn Evals Plan](multi_turn_evals_implementation_plan_v2.md) - Technical implementation details
- [README](README.md) - Project documentation index
