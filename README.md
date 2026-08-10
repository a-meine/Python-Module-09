# Input Validation Comparison

This compares three approaches using the same `User` input:

```python
{
    "name": "Ana",
    "age": "25",
    "email": "ana@example.com"
}
```

The line counts are approximate and exclude imports, blank lines, and formatting.

## 1. Basic type validation

Requirement:

- `name` must be a string.
- `age` must be an integer.
- `email` must be a string.

### Manual dictionary validation

```python
def parse_user(data):
    if "name" not in data:
        raise ValueError("name is required")
    if not isinstance(data["name"], str):
        raise TypeError("name must be a string")

    if "age" not in data:
        raise ValueError("age is required")
    try:
        age = int(data["age"])
    except (TypeError, ValueError):
        raise ValueError("age must be an integer")

    if "email" not in data:
        raise ValueError("email is required")
    if not isinstance(data["email"], str):
        raise TypeError("email must be a string")

    return {
        "name": data["name"],
        "age": age,
        "email": data["email"],
    }
```

**Approximate size: 20 lines**

### Dataclass with manual validation

A standard dataclass only creates the data container. Its annotations do not validate values at runtime, so validation must be added separately, commonly in `__post_init__`.

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    email: str

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise TypeError("name must be a string")

        if not isinstance(self.age, int):
            raise TypeError("age must be an integer")

        if not isinstance(self.email, str):
            raise TypeError("email must be a string")
```

**Approximate size: 14 lines**

The dataclass validates values passed directly to `User`, but it does not automatically parse the original dictionary or convert `"25"` into `25`. That parsing must happen separately.

### Pydantic

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str
```

Pydantic validates the fields at runtime and can parse values such as `"25"` into `25`.

**Approximate size: 5 lines**

## 2. Add value constraints

Requirement:

- `name` cannot be empty.
- `age` must be between 0 and 120.
- `email` must contain `@`.

### Manual dictionary validation

```python
def parse_user(data):
    if "name" not in data:
        raise ValueError("name is required")
    if not isinstance(data["name"], str):
        raise TypeError("name must be a string")
    if not data["name"].strip():
        raise ValueError("name cannot be empty")

    if "age" not in data:
        raise ValueError("age is required")
    try:
        age = int(data["age"])
    except (TypeError, ValueError):
        raise ValueError("age must be an integer")
    if not 0 <= age <= 120:
        raise ValueError("age must be between 0 and 120")

    if "email" not in data:
        raise ValueError("email is required")
    if not isinstance(data["email"], str):
        raise TypeError("email must be a string")
    if "@" not in data["email"]:
        raise ValueError("invalid email")

    return User(
        name=data["name"],
        age=age,
        email=data["email"],
    )
```

**Approximate size: 25 lines**

### Dataclass

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    email: str

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise TypeError("name must be a string")
        if not self.name.strip():
            raise ValueError("name cannot be empty")

        if not isinstance(self.age, int):
            raise TypeError("age must be an integer")
        if not 0 <= self.age <= 120:
            raise ValueError("age must be between 0 and 120")

        if not isinstance(self.email, str):
            raise TypeError("email must be a string")
        if "@" not in self.email:
            raise ValueError("invalid email")
```

**Approximate size: 20 lines**

The dataclass still does not automatically convert `"25"` into `25`. You must parse it before creating the object.

### Pydantic

```python
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0, le=120)
    email: EmailStr
```

**Approximate size: 6 lines**

The constraints are declared directly beside the fields.

## 3. Add custom field logic

Requirement:

- Remove whitespace around the name.
- Convert the email to lowercase.

### Manual dictionary validation

```python
def parse_user(data):
    if "name" not in data:
        raise ValueError("name is required")
    if not isinstance(data["name"], str):
        raise TypeError("name must be a string")

    name = data["name"].strip()
    if not name:
        raise ValueError("name cannot be empty")

    try:
        age = int(data["age"])
    except (TypeError, ValueError):
        raise ValueError("age must be an integer")

    if not 0 <= age <= 120:
        raise ValueError("age must be between 0 and 120")

    email = data["email"].strip().lower()
    if "@" not in email:
        raise ValueError("invalid email")

    return User(name=name, age=age, email=email)
```

**Approximate size: 18 lines**

### Dataclass

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    email: str

    def __post_init__(self):
        self.name = self.name.strip()
        self.email = self.email.strip().lower()

        if not self.name:
            raise ValueError("name cannot be empty")
        if not isinstance(self.age, int):
            raise TypeError("age must be an integer")
        if not 0 <= self.age <= 120:
            raise ValueError("age must be between 0 and 120")
        if "@" not in self.email:
            raise ValueError("invalid email")
```

**Approximate size: 15 lines**

### Pydantic

```python
from pydantic import BaseModel, Field, EmailStr, field_validator

class User(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0, le=120)
    email: EmailStr

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        return value.strip()

    @field_validator("email")
    @classmethod
    def clean_email(cls, value):
        return str(value).lower()
```

**Approximate size: 14 lines**

Here the difference is smaller because custom business rules require custom code in every approach. Pydantic still provides the basic parsing, standard validation, and consistent error handling.

## 4. Add a rule involving multiple fields

New requirement:

- Add `password` and `password_repeat`.
- Both values must match.

### Manual dictionary validation

```python
def parse_user(data):
    # Validate and parse name, age, and email first
    name = data["name"].strip()
    age = int(data["age"])
    email = data["email"].strip().lower()

    if not name:
        raise ValueError("name cannot be empty")
    if not 0 <= age <= 120:
        raise ValueError("age must be between 0 and 120")
    if "@" not in email:
        raise ValueError("invalid email")

    if "password" not in data:
        raise ValueError("password is required")
    if "password_repeat" not in data:
        raise ValueError("password_repeat is required")
    if data["password"] != data["password_repeat"]:
        raise ValueError("passwords do not match")

    return User(
        name=name,
        age=age,
        email=email,
        password=data["password"],
        password_repeat=data["password_repeat"],
    )
```

**Approximate size: 25+ lines**

### Dataclass

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    email: str
    password: str
    password_repeat: str

    def __post_init__(self):
        self.name = self.name.strip()
        self.email = self.email.strip().lower()

        if not self.name:
            raise ValueError("name cannot be empty")
        if not 0 <= self.age <= 120:
            raise ValueError("age must be between 0 and 120")
        if "@" not in self.email:
            raise ValueError("invalid email")
        if self.password != self.password_repeat:
            raise ValueError("passwords do not match")
```

**Approximate size: 18 lines**

### Pydantic

```python
from pydantic import BaseModel, Field, EmailStr, model_validator

class User(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0, le=120)
    email: EmailStr
    password: str
    password_repeat: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.password_repeat:
            raise ValueError("passwords do not match")
        return self
```

**Approximate size: 15 lines**

## Size comparison

| Case | Manual `if` statements | Dataclass | Pydantic |
|---|---:|---:|---:|
| Basic types | ~20 lines | ~14 lines | ~5 lines |
| Type and value constraints | ~25 lines | ~20 lines | ~6 lines |
| Custom field transformations | ~18 lines | ~15 lines | ~14 lines |
| Cross-field validation | ~25+ lines | ~18 lines | ~15 lines |
| Automatic string-to-type parsing | You implement it | You implement it | Built in for common cases |
| Structured validation errors | You implement it | You implement it | Built in |
| Runtime validation from annotations | No | No, unless you add it | Yes |

## The practical conclusion

Pydantic is not always dramatically shorter. Its biggest advantage is that it gives you a **standard validation system**:

- Simple types and constraints require very little code.
- Complex business rules still require custom functions.
- Parsing, error formatting, nested models, and serialization are handled consistently.
- The model itself documents the expected input.

A useful rule is:

> Use a `dataclass` for trusted internal data. Use Pydantic when data enters your program from an untrusted or external source. Use manual `if` statements when the validation is small and one-off.
