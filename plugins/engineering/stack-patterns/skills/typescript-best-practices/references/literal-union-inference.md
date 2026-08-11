# Literal Union Inference

Use a `const enum` when a named closed primitive state set needs to survive beyond one local expression. Do not annotate a string-literal union merely to widen an initial state value.

```typescript
// BAD: Infer a State Setter From Only Its Initial Member
const enum RequestStatus {
	Idle = 'idle',
	Loading = 'loading',
	Error = 'error',
}

const [state, setState] = useState(RequestStatus.Idle);

setState(RequestStatus.Loading);
// Error: RequestStatus.Loading is not assignable to RequestStatus.Idle.
```

```typescript
// GOOD: Declare the Intended State Set at the Inference Boundary
const enum RequestStatus {
	Idle = 'idle',
	Loading = 'loading',
	Error = 'error',
}

const [state, setState] = useState<RequestStatus>(RequestStatus.Idle);
setState(RequestStatus.Loading);
```

The explicit generic is necessary because the state must represent more members than its initial value.

Use an explicit type when an API cannot infer its intended value shape.

```typescript
// `createContext` infers only null without the intended value type.
const Context = createContext<UserContextValue | null>(null);
```

Keep an ad-hoc conditional expression unannotated. TypeScript already infers its local literal union.

```typescript
const viewMode = isDetail ? 'detail' : 'list';
// inferred: "detail" | "list"
```
