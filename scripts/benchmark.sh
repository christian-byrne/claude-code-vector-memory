#!/bin/bash
# Performance benchmarking for semantic memory system

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

echo "⏱️  Semantic Memory System Benchmark"
echo "====================================="

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found!"
    exit 1
fi

# Check if system is ready
if [ ! -d "chroma_db" ]; then
    echo "❌ Database not found. Please run ./setup.sh first"
    exit 1
fi

echo "🔍 Running comprehensive benchmarks..."

# Test queries for benchmarking
TEST_QUERIES=(
    "vue component implementation"
    "typescript type safety"
    "python script automation"
    "git commit workflow"
    "testing vitest setup"
    "frontend ui design"
    "api endpoint creation"
    "database optimization"
    "error handling patterns"
    "performance tuning"
)

echo ""
echo "📊 Search Performance Benchmark"
echo "================================"

TOTAL_TIME=0
TOTAL_QUERIES=${#TEST_QUERIES[@]}

for i in "${!TEST_QUERIES[@]}"; do
    query="${TEST_QUERIES[$i]}"
    echo -n "Query $((i+1))/$TOTAL_QUERIES: '$query' ... "
    
    # Time the search
    start_time=$(python3 -c "import time; print(time.time())")
    
    # Run the search (capture output to avoid clutter)
    python scripts/memory_search.py "$query" > /dev/null 2>&1
    
    end_time=$(python3 -c "import time; print(time.time())")
    
    # Calculate duration in milliseconds
    duration=$(python3 -c "print(int(($end_time - $start_time) * 1000))")
    TOTAL_TIME=$((TOTAL_TIME + duration))
    
    echo "${duration}ms"
done

# Calculate average
AVERAGE_TIME=$((TOTAL_TIME / TOTAL_QUERIES))

echo ""
echo "📈 Performance Summary"
echo "======================"
echo "Total queries: $TOTAL_QUERIES"
echo "Total time: ${TOTAL_TIME}ms"
echo "Average time: ${AVERAGE_TIME}ms per query"

# Performance rating
if [ $AVERAGE_TIME -lt 100 ]; then
    echo "🚀 Performance: Excellent (< 100ms)"
elif [ $AVERAGE_TIME -lt 200 ]; then
    echo "✅ Performance: Good (< 200ms)"
elif [ $AVERAGE_TIME -lt 500 ]; then
    echo "⚠️  Performance: Acceptable (< 500ms)"
else
    echo "🐌 Performance: Needs optimization (> 500ms)"
fi

echo ""
echo "🔬 System Resource Usage"
echo "========================"

# Database size
if [ -d "chroma_db" ]; then
    DB_SIZE=$(du -sh chroma_db/ | cut -f1)
    echo "Database size: $DB_SIZE"
fi

# Memory usage (rough estimate)
echo "Python process memory usage:"
ps aux | grep python | grep -v grep | head -3

echo ""
echo "🧪 Health Check Results"
echo "======================="

# Run health check for additional metrics
python scripts/health_check.py

echo ""
echo "💡 Performance Recommendations"
echo "==============================="

if [ $AVERAGE_TIME -gt 200 ]; then
    echo "• Consider using a smaller embedding model for faster searches"
    echo "• Check system resources (CPU, memory, disk I/O)"
    echo "• Reduce the number of indexed summaries if not needed"
fi

echo "• Regular reindexing can improve performance"
echo "• Keep database size under 100MB for optimal performance"
echo "• Use specific search terms for better results"

echo ""
echo "✅ Benchmark complete!"