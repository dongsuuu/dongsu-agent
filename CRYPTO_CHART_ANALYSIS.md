# 암호화폐 차트 오픈소스 분석

## 1. TradingView Lightweight Charts

### 핵심 특징
- **크기**: ~40KB (gzip)
- **성능**: Canvas 기반, 60fps
- **시리즈 타입**: Line, Area, Bar, Candlestick, Histogram, Baseline

### Best Practices
```typescript
// 1. Chart 생성
const chart = createChart(container, {
  layout: { background: { type: ColorType.Solid, color: '#131722' } },
  grid: { vertLines: { color: '#2B2B43' }, horzLines: { color: '#2B2B43' } },
  crosshair: { mode: CrosshairMode.Normal },
  rightPriceScale: { borderColor: '#2B2B43' },
  timeScale: { borderColor: '#2B2B43', timeVisible: true },
});

// 2. Series 추가
const candleSeries = chart.addSeries(CandlestickSeries, {
  upColor: '#26a69a', downColor: '#ef5350',
  borderUpColor: '#26a69a', borderDownColor: '#ef5350',
  wickUpColor: '#26a69a', wickDownColor: '#ef5350',
});

// 3. 데이터 설정
candleSeries.setData([
  { time: '2018-12-22', open: 75.16, high: 82.84, low: 36.16, close: 45.72 },
  // ...
]);

// 4. 실시간 업데이트
candleSeries.update({ time: '2018-12-22', open: 75.16, high: 82.84, low: 36.16, close: 45.72 });
```

### 이벤트 처리
```typescript
// Crosshair 이동
chart.subscribeCrosshairMove((param) => {
  if (param.time && param.point) {
    const data = param.seriesData.get(candleSeries);
    console.log(data); // { open, high, low, close, time }
  }
});

// 클릭
chart.subscribeClick((param) => {
  console.log('Clicked at:', param.time);
});

// Visible range 변경 (무한 스크롤)
chart.timeScale().subscribeVisibleLogicalRangeChange((range) => {
  if (range && range.from < 50) {
    // 과거 데이터 로드
  }
});
```

---

## 2. Uniswap Interface

### 아키텍처 패턴
```typescript
// ChartModel 기반 추상화
abstract class ChartModel<T> {
  protected api: IChartApi;
  protected series: ISeriesApi;
  protected data: T[];
  
  abstract updateData(data: T[]): void;
  abstract getHoverCoordinates(): { x: number; y: number } | null;
}

// PriceChartModel 구현
class PriceChartModel extends ChartModel<PriceChartData> {
  private type: PriceChartType;
  private minPriceLine: IPriceLine;
  private maxPriceLine: IPriceLine;
  
  // 캔들스틱/라인 차트 타입 지원
  initSeries() {
    if (this.type === PriceChartType.CANDLESTICK) {
      this.series = this.api.addSeries(RoundedCandleSeries, options);
    } else {
      this.series = this.api.addSeries(AreaSeries, options);
    }
  }
}
```

### 스타일링 (Tamagui)
```typescript
export const ChartTooltip = styled(Flex, {
  alignItems: 'center',
  position: 'absolute',
  left: 0, top: 0,
  zIndex: '$tooltip',
  pointerEvents: 'none', // 툴팁이 마우스 이벤트 차단 방지
  variants: {
    includeBorder: {
      true: {
        backgroundColor: '$surface5',
        backdropFilter: 'blur(8px)',
        borderRadius: '$rounded8',
        borderColor: '$surface3',
        borderWidth: 1,
      },
    },
  },
});
```

### 데이터 포맷팅
```typescript
// 저가 범위 처리 (스테이블코인 등)
const LOW_PRICE_RANGE_THRESHOLD = 0.2;
const LOW_PRICE_RANGE_SCALE_FACTOR = 1000000000;

if (max - min < LOW_PRICE_RANGE_THRESHOLD) {
  // 스케일 팩터 적용하여 표시
}

// Y축 포맷터
const yAxisFormatter = (price: number) => {
  return price < 0.01 ? price.toExponential(2) : price.toFixed(2);
};
```

---

## 3. 핵심 학습 포인트

### A. 데이터 흐름
```
API → Normalization → ChartModel → Series.setData()
                    ↓
              Real-time Updates
                    ↓
              series.update()
```

### B. 성능 최적화
1. **데이터 캐싱**: 300개씩 페이지네이션
2. **디바운싱**: resize 이벤트 100ms 디바운스
3. **메모이제이션**: 차트 인스턴스 재사용
4. **레이지 로딩**: 동적 import('lightweight-charts')

### C. 에러 핸들링
```typescript
const [chartError, setChartError] = useState<string | null>(null);

try {
  const chart = createChart(container, options);
} catch (error) {
  setChartError('Failed to initialize chart');
  console.error(error);
}

// UI
{chartError && (
  <ErrorContainer>
    <Text color="error">{chartError}</Text>
    <Button onClick={retry}>Retry</Button>
  </ErrorContainer>
)}
```

### D. 반응형 디자인
```typescript
useEffect(() => {
  const handleResize = () => {
    if (containerRef.current && chartRef.current) {
      chartRef.current.applyOptions({
        width: containerRef.current.clientWidth,
        height: containerRef.current.clientHeight,
      });
    }
  };
  
  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize);
}, []);
```

---

## 4. 개선 제안 (dongsu-website용)

### 현재 문제
1. **Store 구조**: Zustand store가 너무 복잡
2. **에러 핸들링**: 부족한 try-catch
3. **타입 안전**: `any` 타입 남용
4. **메모리 누수**: cleanup 함수 불완전

### 개선 방향
```typescript
// 1. 단순화된 Store
interface ChartState {
  symbol: string;
  resolution: string;
  data: CandleData[];
  isLoading: boolean;
  error: Error | null;
}

// 2. 커스텀 훅
function useChartData(symbol: string, resolution: string) {
  const [state, dispatch] = useReducer(chartReducer, initialState);
  
  useEffect(() => {
    const abortController = new AbortController();
    
    fetchData(symbol, resolution, { signal: abortController.signal })
      .then(data => dispatch({ type: 'SET_DATA', payload: data }))
      .catch(err => dispatch({ type: 'SET_ERROR', payload: err }));
    
    return () => abortController.abort();
  }, [symbol, resolution]);
  
  return state;
}

// 3. 차트 컴포넌트
const Chart = memo(function Chart({ data }: { data: CandleData[] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  
  useEffect(() => {
    if (!containerRef.current) return;
    
    chartRef.current = createChart(containerRef.current, options);
    const series = chartRef.current.addSeries(CandlestickSeries, seriesOptions);
    series.setData(data);
    
    return () => {
      chartRef.current?.remove();
      chartRef.current = null;
    };
  }, []);
  
  useEffect(() => {
    const series = chartRef.current?.getSeries();
    series?.setData(data);
  }, [data]);
  
  return <div ref={containerRef} className="w-full h-full" />;
});
```

---

## 5. 참고 리소스

- [Lightweight Charts Docs](https://tradingview.github.io/lightweight-charts/)
- [Uniswap Interface GitHub](https://github.com/Uniswap/interface)
- [React Stockcharts](https://github.com/rrag/react-stockcharts) (D3 기반)
- [Vega Protocol](https://github.com/vegaprotocol/frontend-monorepo)
