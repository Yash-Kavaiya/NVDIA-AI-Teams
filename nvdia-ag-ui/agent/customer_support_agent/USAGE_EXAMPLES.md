# Customer Support Agent - Usage Examples

Real-world examples demonstrating the customer support agent's capabilities.

## 📋 Table of Contents

1. [Basic Policy Questions](#basic-policy-questions)
2. [Specific Product Queries](#specific-product-queries)
3. [Complex Multi-Part Questions](#complex-multi-part-questions)
4. [Edge Cases](#edge-cases)
5. [Tool Testing](#tool-testing)
6. [API Integration](#api-integration)

---

## Basic Policy Questions

### Example 1: General Return Policy

**User Query:**
```
What is your return policy?
```

**Agent Response:**
```
**Return Policy Overview**:

According to our Returns and Exchanges Policy (chunk 3):
"Customers may return most items within 30 days of purchase for a full 
refund or exchange. Items must be in original condition with tags attached 
and proof of purchase."

**Key Points**:
- Return window: 30 days from purchase date
- Condition: Original packaging and tags required
- Proof of purchase: Receipt or order confirmation needed
- Refund method: Original payment method

**Exceptions**:
- Opened software/media: No returns
- Intimate apparel: Final sale
- Sale items: Store credit only

**Confidence**: 0.89/1.0 (Rerank Score)
**Source**: Returns_and_Exchanges_Policy_2024.pdf, Section 2.1
```

---

### Example 2: Electronics Returns

**User Query:**
```
Can I return my laptop? I bought it 2 weeks ago.
```

**Agent Response:**
```
**Electronics Return Policy**:

Yes, you can return your laptop! According to our Electronics Return 
Policy (chunk 8):

"Electronic items including computers and laptops may be returned within 
30 days of purchase. Items must include original packaging, all 
accessories, manuals, and be in new, unused condition."

**Requirements for Your Return**:
✅ Within 30-day window (you're at 2 weeks)
✅ Original packaging and accessories
✅ Receipt or proof of purchase
⚠️ Note: 15% restocking fee applies if opened

**Process**:
1. Bring laptop with all original items
2. Present receipt
3. Receive refund minus restocking fee (if opened)

**Confidence**: 0.94/1.0 (Rerank Score)
**Source**: Electronics_Return_Policy_v3.pdf, Section 1.2
```

---

## Specific Product Queries

### Example 3: Clothing Returns

**User Query:**
```
What if the dress I bought doesn't fit? Can I exchange it?
```

**Agent Response:**
```
**Clothing Exchange Policy**:

Yes, you can exchange your dress! According to our Apparel Return and 
Exchange Guidelines (chunk 5):

"All clothing items may be exchanged for a different size or color within 
30 days. Exchanges are free with original tags and receipt."

**Exchange Options**:
1. **Different Size**: Free exchange, same item
2. **Different Color**: Free exchange, same item
3. **Different Item**: Subject to price difference

**Requirements**:
✅ Original tags attached
✅ Unworn and unwashed condition
✅ Receipt or proof of purchase
✅ Within 30 days of purchase

**How to Exchange**:
- In-store: Bring item + receipt to any location
- Online: Initiate exchange through account portal
- Processing: 3-5 business days for online exchanges

**Confidence**: 0.91/1.0 (Rerank Score)
**Source**: Apparel_Guidelines_2024.pdf, Section 3.4
```

---

### Example 4: Warranty Questions

**User Query:**
```
Do washing machines come with a warranty?
```

**Agent Response:**
```
**Appliance Warranty Coverage**:

Yes! Washing machines include comprehensive warranty coverage. According 
to our Appliance Warranty Terms (chunk 12):

"Major appliances including washing machines come with:
- 1-year manufacturer warranty (parts and labor)
- Optional extended warranty available for purchase
- Covers defects in materials and workmanship"

**What's Covered**:
✅ Mechanical failures
✅ Electrical issues
✅ Parts replacement
✅ Labor costs for repairs

**What's NOT Covered**:
❌ Normal wear and tear
❌ Customer misuse or damage
❌ Installation issues
❌ Cosmetic damage

**Extended Warranty Options**:
- 2-year extended: $149
- 3-year extended: $229
- 5-year extended: $349

**How to Make a Claim**:
1. Contact customer service: 1-800-XXX-XXXX
2. Provide model number and purchase date
3. Schedule technician visit (if needed)

**Confidence**: 0.88/1.0 (Rerank Score)
**Source**: Appliance_Warranty_2024.pdf, Section 4.1 & 4.3
```

---

## Complex Multi-Part Questions

### Example 5: Multi-Condition Query

**User Query:**
```
I bought shoes 3 weeks ago, wore them once, but they're uncomfortable. 
Can I return them even though they've been worn?
```

**Agent Response:**
```
**Worn Footwear Return Policy**:

This is a nuanced situation. According to our Footwear Return Guidelines 
(chunk 7):

"Footwear may be returned within 30 days if showing only minor indoor 
wear. Shoes showing excessive wear, outdoor damage, or significant 
scuffing are not eligible for return."

**Your Situation Analysis**:
✅ Within 30-day window (3 weeks)
⚠️ Worn once - depends on condition
❌ If shoes show significant wear marks

**Eligibility Criteria**:
1. **Acceptable**: Minor indoor wear, clean soles, no scuffs
2. **Not Acceptable**: Outdoor wear, dirty soles, visible damage

**Recommendation**:
Bring the shoes to a store for assessment. Our team will evaluate:
- Sole condition
- Upper material condition
- Overall appearance

**Alternative Options**:
If not eligible for return, you may be eligible for:
- Store credit (manager discretion)
- Exchange for different size
- Comfort insole fitting service

**Confidence**: 0.83/1.0 (Rerank Score)
**Source**: Footwear_Guidelines_2024.pdf, Section 2.3
**Note**: Final decision subject to in-store evaluation
```

---

### Example 6: Without Receipt

**User Query:**
```
Can I return something without a receipt? I lost it.
```

**Agent Response:**
```
**No-Receipt Return Policy**:

Yes, but with limitations. According to our Return Policy Without Receipt 
(chunk 15):

"Returns without receipt are accepted under the following conditions:
- Valid government-issued ID required
- Store credit only (no cash refunds)
- Limited to $50 per 30-day period
- Item must be in current inventory
- Final sale and clearance items excluded"

**How It Works**:
1. **Verification**: ID scanned to track returns
2. **Price Match**: Current selling price (not purchase price)
3. **Store Credit**: Issued as merchandise credit
4. **Tracking**: System monitors frequency to prevent abuse

**Better Options**:
- Check email for digital receipt
- Look up with credit card used
- Check online account order history
- Contact original store of purchase

**Important Limits**:
⚠️ Maximum: $50 per month without receipt
⚠️ Some items excluded: Electronics, jewelry, cosmetics
⚠️ Excessive returns may be declined

**Confidence**: 0.90/1.0 (Rerank Score)
**Source**: Returns_Policy_2024.pdf, Section 5.2
```

---

## Edge Cases

### Example 7: Sale Items

**User Query:**
```
Are final sale items really final? No exceptions?
```

**Agent Response:**
```
**Final Sale Policy**:

According to our Sale Item Return Policy (chunk 9):

"Items marked 'Final Sale' or 'Clearance' are not eligible for return 
or exchange except in cases of:
1. Defective merchandise
2. Incorrect item shipped (online orders)
3. Item significantly different from description"

**Exceptions That Allow Returns**:
✅ **Defective**: Manufacturing defect present at purchase
✅ **Wrong Item**: We shipped wrong product
✅ **Misrepresented**: Item materially different from listing

**NOT Eligible**:
❌ Changed mind
❌ Size doesn't fit
❌ Color not as expected
❌ Found better price elsewhere

**Important Notes**:
- Final sale items clearly marked with signage/tags
- Online: Noted on product page in red text
- Sale percentages don't automatically mean final sale
- Regular sale items (not marked final) follow standard return policy

**Recommendation**:
- Try items in-store when possible for final sale
- Check measurements carefully for clothing
- Read product descriptions thoroughly for online orders

**Confidence**: 0.92/1.0 (Rerank Score)
**Source**: Sale_Items_Policy_2024.pdf, Section 1.1 & 1.4
```

---

### Example 8: Gift Returns

**User Query:**
```
Someone gave me a gift but I don't have a receipt. What can I do?
```

**Agent Response:**
```
**Gift Return Policy**:

Great news! According to our Gift Return and Exchange Policy (chunk 11):

"Gift recipients may exchange or return items without a receipt. 
Requirements:
- Item must be unopened/unused (or worn once for footwear/apparel)
- Tags still attached
- Clearly a gift purchase (gift receipt or gift box)
- Exchange for same or lesser value, or store credit"

**Your Options**:
1. **Exchange**: For any item of equal/lesser value
2. **Store Credit**: Full merchandise credit at current price
3. **Gift Card**: Convert store credit to gift card

**Process**:
1. Bring gift item with tags to any store
2. No ID required for exchanges
3. Store credit issued if desired
4. Valid for 1 year from issue date

**Cannot Do**:
❌ Cash refund without original receipt
❌ Return opened electronics or software
❌ Return intimate apparel or cosmetics

**Pro Tip**: 
Ask gift giver to forward gift receipt email - provides more flexibility 
and shows original purchase price.

**Confidence**: 0.86/1.0 (Rerank Score)
**Source**: Gift_Returns_Policy_2024.pdf, Section 2.1
```

---

## Tool Testing

### Example 9: Direct Tool Call

**Python Code:**
```python
from customer_support_agent.tools import search_policy_documents

# Basic search
result = search_policy_documents(
    query="What is the shipping policy?",
    top_k=3
)

print(f"Found {result['results_count']} results")
for doc in result['results']:
    print(f"\n{doc['rank']}. {doc['source_filename']}")
    print(f"   Score: {doc['rerank_score']:.2f}")
    print(f"   Text: {doc['text'][:100]}...")
```

**Output:**
```
Found 3 results

1. Shipping_Policy_2024.pdf
   Score: 0.94
   Text: Standard shipping is FREE on orders over $50. Orders under $50 incur a $7.95 shipping fee...

2. Delivery_Options_2024.pdf
   Score: 0.87
   Text: We offer multiple shipping speeds: Standard (5-7 days), Express (2-3 days), Overnight (1 day)...

3. International_Shipping_v2.pdf
   Score: 0.72
   Text: International orders ship via DHL or FedEx. Customs fees may apply depending on destination...
```

---

### Example 10: Collection Info

**Python Code:**
```python
from customer_support_agent.tools import get_collection_info

info = get_collection_info()

if info['success']:
    print(f"Collection: {info['collection_name']}")
    print(f"Total chunks: {info['total_chunks']}")
    print(f"Status: {info['status']}")
    print(f"Vector size: {info['vector_size']}")
```

**Output:**
```
Collection: customer_support_docs
Total chunks: 187
Status: green
Vector size: 2048
```

---

## API Integration

### Example 11: REST API Call

**cURL Command:**
```bash
curl -X POST http://localhost:3000/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "What is your return policy for electronics?"
      }
    ],
    "agent": "customer_support_agent"
  }'
```

**Response:**
```json
{
  "message": {
    "role": "assistant",
    "content": "**Electronics Return Policy**:\n\nAccording to our Electronics Return Policy (chunk 8):\n\"Electronic items may be returned within 30 days...\"\n\n**Confidence**: 0.94/1.0\n**Source**: Electronics_Return_Policy_v3.pdf"
  },
  "metadata": {
    "agent": "customer_support_agent",
    "tools_used": ["search_policy_documents"],
    "confidence": 0.94,
    "sources": ["Electronics_Return_Policy_v3.pdf"]
  }
}
```

---

### Example 12: Multi-Turn Conversation

**Conversation Flow:**

**User:** "What is your return policy?"

**Agent:** *(Provides general return policy overview)*

**User:** "What about electronics specifically?"

**Agent:** *(Provides electronics-specific policy, referencing earlier context)*

**User:** "Can I return an opened laptop?"

**Agent:** 
```
**Opened Electronics Return**:

Based on our discussion of the electronics return policy, here's what 
applies to opened laptops:

According to Electronics Return Policy (chunk 8):
"Opened electronics may be returned within 30 days but are subject to 
a 15% restocking fee. The item must be in like-new condition with all 
original packaging, accessories, and documentation."

**For Your Opened Laptop**:
✅ Returnable within 30 days
⚠️ 15% restocking fee applies
✅ Must have all original items

**Calculation Example**:
- Laptop price: $1,000
- Restocking fee: $150 (15%)
- Refund amount: $850

**To Avoid Restocking Fee**:
Unfortunately, once opened, the fee applies. However, you may consider:
- Exchange for different model (no fee)
- Store credit instead of refund (no fee)

**Confidence**: 0.91/1.0
**Source**: Electronics_Return_Policy_v3.pdf, Section 1.3
```

---

## Success Metrics

Track these metrics for quality assurance:

| Metric | Example Value | Interpretation |
|--------|--------------|----------------|
| Rerank Score | 0.92 | Excellent match |
| Vector Score | 0.87 | Good semantic similarity |
| Response Time | 2.3s | Acceptable speed |
| Citation Present | Yes | ✅ Quality response |
| Source Valid | Yes | ✅ Traceable |

---

## Best Practices Demonstrated

1. ✅ **Always cite sources** - Every response includes document reference
2. ✅ **Show confidence** - Rerank and vector scores displayed
3. ✅ **Be transparent** - Clear about policy limitations and exceptions
4. ✅ **Provide alternatives** - Offer options when primary request not possible
5. ✅ **Use structured format** - Organized, scannable responses
6. ✅ **Include specifics** - Exact policy language, not paraphrasing
7. ✅ **Context-aware** - Reference previous conversation when relevant
8. ✅ **Helpful tone** - Professional but friendly and supportive

---

## Next Steps

Want to try these examples?

1. **Setup**: Follow [QUICKSTART.md](./QUICKSTART.md)
2. **Add Documents**: Place your PDFs in `customer_support/data/`
3. **Process**: Run `python main.py process ./data`
4. **Test**: Run `python test_agent.py`
5. **Use**: Start app with `npm run dev`

---

**Need custom examples for your use case?** See [README.md](./README.md) for customization guide.
