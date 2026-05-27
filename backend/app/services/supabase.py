"""Supabase HTTP API 封装（不依赖 supabase-py，避免编译问题）"""
import httpx
from app.config import settings


class SupabaseAPI:
    def __init__(self):
        self.url = settings.supabase_url
        self.key = settings.supabase_service_key
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }

    # --- Auth ---
    def auth_signup(self, email: str, password: str, metadata: dict):
        r = httpx.post(f"{self.url}/auth/v1/signup", headers={**self.headers, "apikey": settings.supabase_anon_key or self.key},
                       json={"email": email, "password": password, "data": metadata})
        r.raise_for_status()
        return r.json()

    def auth_login(self, email: str, password: str):
        r = httpx.post(f"{self.url}/auth/v1/token?grant_type=password", headers={**self.headers, "apikey": settings.supabase_anon_key or self.key},
                       json={"email": email, "password": password})
        r.raise_for_status()
        return r.json()

    # --- Table CRUD (PostgREST) ---
    def select(self, table: str, columns: str = "*"):
        return SupabaseQuery(self, table, columns)

    def insert(self, table: str, data: dict | list):
        headers = {**self.headers, "Prefer": "return=representation"}
        r = httpx.post(f"{self.url}/rest/v1/{table}", headers=headers, json=data)
        r.raise_for_status()
        return r.json() if r.text else []

    def update(self, table: str, data: dict, match: dict):
        headers = {**self.headers, "Prefer": "return=representation"}
        r = httpx.patch(f"{self.url}/rest/v1/{table}", headers=headers, json=data, params=match)
        r.raise_for_status()
        return r.json() if r.text else []

    def delete(self, table: str, match: dict):
        headers = {**self.headers, "Prefer": "return=representation"}
        r = httpx.delete(f"{self.url}/rest/v1/{table}", headers=headers, params=match)
        r.raise_for_status()
        return r.json() if r.text else []

    # --- Storage ---
    def storage_upload(self, bucket: str, path: str, data: bytes, content_type: str = "image/jpeg"):
        headers = {"apikey": self.key, "Authorization": f"Bearer {self.key}"}
        r = httpx.post(f"{self.url}/storage/v1/object/{bucket}/{path}", headers=headers, content=data,
                       params={"content-type": content_type})
        if r.status_code == 400 and "not found" in r.text.lower():
            # bucket 不存在，先创建
            httpx.post(f"{self.url}/storage/v1/bucket", headers={**headers, "Content-Type": "application/json"},
                       json={"id": bucket, "name": bucket, "public": True})
            r = httpx.post(f"{self.url}/storage/v1/object/{bucket}/{path}", headers=headers, content=data)
        r.raise_for_status()
        return r.json() if r.text else {}

    def storage_public_url(self, bucket: str, path: str) -> str:
        return f"{self.url}/storage/v1/object/public/{bucket}/{path}"

    def create_bucket(self, name: str):
        headers = {"apikey": self.key, "Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        r = httpx.post(f"{self.url}/storage/v1/bucket", headers=headers, json={"id": name, "name": name, "public": True})
        return r.json() if r.text else {}


class SupabaseQuery:
    def __init__(self, api: SupabaseAPI, table: str, columns: str = "*"):
        self.api = api
        self.table = table
        self.select_cols = columns
        self._filters = []
        self._order_col = None
        self._order_dir = "asc"
        self._limit_val = None
        self._single = False

    def eq(self, col: str, val):
        self._filters.append((col, f"eq.{val}"))
        return self

    def in_(self, col: str, vals: list):
        vals_str = ",".join(str(v) for v in vals)
        self._filters.append((col, f"in.({vals_str})"))
        return self

    def order(self, col: str, *, asc: bool = True):
        self._order_col = col
        self._order_dir = "asc" if asc else "desc"
        return self

    def limit(self, n: int):
        self._limit_val = n
        return self

    def single(self):
        self._single = True
        return self

    def execute(self):
        url = f"{self.api.url}/rest/v1/{self.table}"
        params = {"select": self.select_cols}
        for col, val in self._filters:
            params[col] = val
        if self._order_col:
            params["order"] = f"{self._order_col}.{self._order_dir}"
        if self._limit_val:
            params["limit"] = str(self._limit_val)

        headers = {**self.api.headers, "Accept": "application/json"}
        r = httpx.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()
        if self._single:
            data = data[0] if data else None
        # 返回类似 supabase-py 的结构
        return SupabaseResult(data)


class SupabaseResult:
    def __init__(self, data):
        self.data = data


# 全局实例
_supabase: SupabaseAPI | None = None


def get_supabase() -> SupabaseAPI:
    global _supabase
    if _supabase is None:
        _supabase = SupabaseAPI()
    return _supabase
