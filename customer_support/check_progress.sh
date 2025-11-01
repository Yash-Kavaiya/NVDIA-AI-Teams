#!/bin/bash
# Script to monitor document processing progress

echo "==============================================="
echo "Document Processing Progress Monitor"
echo "==============================================="
echo ""

# Check if processes are running
echo "📊 Checking running processes..."
ps aux | grep "process_single.py" | grep -v grep | wc -l | xargs -I {} echo "Active processes: {}"
echo ""

# Check log files
echo "📄 Log file status:"
echo ""

if [ -f "logs/2015-31795.log" ]; then
    echo "--- 2015-31795.pdf ---"
    echo "Log size: $(du -h logs/2015-31795.log | cut -f1)"
    echo "Last 3 lines:"
    tail -n 3 logs/2015-31795.log
    echo ""
fi

if [ -f "logs/RegulatedProductsHandbook.log" ]; then
    echo "--- RegulatedProductsHandbook.pdf ---"
    echo "Log size: $(du -h logs/RegulatedProductsHandbook.log | cut -f1)"
    echo "Last 3 lines:"
    tail -n 3 logs/RegulatedProductsHandbook.log
    echo ""
fi

# Check Qdrant collection
echo "📦 Qdrant Collection Status:"
curl -s http://localhost:6333/collections/customer_support_docs | python -c "import sys, json; data=json.load(sys.stdin); print(f\"Total points: {data['result']['points_count']}\")"
echo ""
echo "==============================================="
