# Motivating Example

Consider a 3D vector used as a direction. A direction must be finite, non-zero, and normalized, but an ordinary `Vec3` communicates none of those invariants.

```rust
#[derive(Clone, Copy)]
struct Vec3 {
    x: f32,
    y: f32,
    z: f32,
}

impl Vec3 {
    fn length(self) -> f32 {
        self.x.hypot(self.y).hypot(self.z)
    }

    fn normalize(self) -> Self {
        let length = self.length(); // Nothing guarantees that this is non-zero!
        Self {
            x: self.x / length,
            y: self.y / length,
            z: self.z / length,
        }
    }
}

fn main() {
    let zero = Vec3 { x: 0.0, y: 0.0, z: 0.0 };
    let _ = zero.normalize(); // Division by zero!
}
```

## Hazard: Normalization is Fallible

Normalization divides by the vector's length. A zero-length vector has no direction, so normalization must fail. Returning another ordinary `Vec3` forces every direction-consuming function to defend itself. In the failure case, a sentinel value like `None` (or worse, `NaN` or some other invalid value) must be propagated back to the caller.

```rust
impl Vec3 {
    fn try_normalize(self) -> Option<Self> {
        let length = self.length();
        if length == 0.0 || !length.is_finite() {
            return None; // necessary defensive programming
        }

        Some(Self {
            x: self.x / length,
            y: self.y / length,
            z: self.z / length,
        })
    }
}

fn cast_ray(origin: Vec3, direction: Vec3) -> Option<Vec3> {
    let direction = direction.try_normalize()?; // This caller must defend itself.
    todo!()
}

fn illuminate_surface(normal: Vec3) -> Option<Vec3> {
    let normal = normal.try_normalize()?; // This caller repeats the same defense!
    todo!()
}
```

## Solution: Introduce a Validated Type Wrapper

Represent the runtime invariant with a distinct type. Keep its field private so that callers can obtain a `NormalizedVec3` only through validation.

```rust
#[derive(Clone, Copy)]
pub struct Vec3 {
    pub x: f32,
    pub y: f32,
    pub z: f32,
}

#[derive(Clone, Copy)]
pub struct NormalizedVec3(Vec3); // Private field: callers cannot forge the proof.

#[derive(Debug, PartialEq)]
pub enum NormalizeError {
    NonFinite,
    ZeroLength,
}

impl TryFrom<Vec3> for NormalizedVec3 {
    type Error = NormalizeError;

    fn try_from(value: Vec3) -> Result<Self, Self::Error> {
        let length = value.x.hypot(value.y).hypot(value.z);
        if !length.is_finite() {
            return Err(NormalizeError::NonFinite); // Defend only at construction.
        }
        if length == 0.0 {
            return Err(NormalizeError::ZeroLength); // Normalization is fallible!
        }

        Ok(Self(Vec3 { // Success establishes the invariant.
            x: value.x / length,
            y: value.y / length,
            z: value.z / length,
        }))
    }
}

impl NormalizedVec3 {
    /// Only the getter is exposed to preserve the invariant.
    pub fn get(self) -> Vec3 {
        self.0
    }
}
```

```rust
fn cast_ray(origin: Vec3, direction: NormalizedVec3) { // The signature demands proof!
    let direction = direction.get(); // No defensive check is necessary.
    // Cast the ray.
}

fn illuminate_surface(normal: NormalizedVec3) { // This function also demands proof.
    let normal = normal.get(); // Still no defensive check.
    // Compute the lighting.
}
```

The constructor owns the defensive check. Every function that accepts `NormalizedVec3` can rely on that proof. Keep the wrapped `Vec3` private and do not expose mutable access that could violate the invariant.

This technique can encode even stronger relationships when the domain benefits from them. For example, a type that proves two normalized vectors are perpendicular can expose a cross product that returns `NormalizedVec3` without another fallible normalization. Such proof types move even relational runtime invariants into function signatures, at the cost of a more elaborate type model.

Use a validated wrapper for a value invariant. Use a proof-of-completion token when the invariant instead records that a required operation occurred.
