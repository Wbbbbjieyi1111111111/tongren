"""快速验证所有 API 端点"""
import json
import urllib.request

BASE = "http://127.0.0.1:8000/api/v1"

def get(path):
    r = urllib.request.urlopen(f"{BASE}{path}").read().decode()
    return json.loads(r)

def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=data,
                                  headers={"Content-Type": "application/json"}, method="POST")
    r = urllib.request.urlopen(req).read().decode()
    return json.loads(r)

def summary(j):
    if j.get("code") != 0:
        return f"FAIL code={j.get('code')} msg={j.get('message','')[:40]}"
    d = j.get("data") or {}
    if isinstance(d, dict):
        if "list" in d and isinstance(d["list"], list):
            return f"list={len(d['list'])}"
        if "total" in d:
            return f"total={d['total']}"
        if "updatedAt" in d:
            return f"updatedAt={d['updatedAt']}"
        keys = list(d.keys())[:8]
        return "keys=" + ",".join(keys)
    return str(d)[:60]

tests_get = [
    "/spots?pageSize=5",
    "/spots/1",
    "/spots/1/related",
    "/routes",
    "/routes/1",
    "/foods",
    "/folk",
    "/festivals",
    "/ethnic",
    "/seasons",
    "/banners",
    "/notices",
    "/search?q=梵净",
    "/analytics/all",
    "/analytics/overview",
    "/analytics/trend",
    "/analytics/ranking",
    "/analytics/heat",
    "/analytics/prediction",
    "/health",
]

print("=" * 60)
print(" 后端接口验证")
print("=" * 60)
passed = 0
for t in tests_get:
    try:
        j = get(t)
        ok = j.get("code") == 0
        mark = "✅" if ok else "❌"
        s = summary(j)
        if ok: passed += 1
    except Exception as e:
        mark = "❌"
        s = f"ERROR {e}"
    print(f"  {mark} {t:35s} {s}")

# 登录
print()
print("  [POST] /user/login  phone=13800000001  password=123456")
try:
    j = post("/user/login", {"phone": "13800000001", "password": "123456"})
    if j.get("code") == 0:
        token = j["data"]["token"]
        user = j["data"]["user"]
        print(f"  ✅ 登录成功 token={token[:20]}... user={user['nickname']}")
        passed += 1

        # 测试需要鉴权的接口
        print()
        print("  [GET] /user/favorites  (带 token)")
        req = urllib.request.Request(f"{BASE}/user/favorites",
                                      headers={"Authorization": f"Bearer {token}"})
        j2 = json.loads(urllib.request.urlopen(req).read().decode())
        ok2 = j2.get("code") == 0
        print(f"  {'✅' if ok2 else '❌'} favorites: spotIds={j2.get('data',{}).get('spotIds',[])} routeIds={j2.get('data',{}).get('routeIds',[])}")
        if ok2: passed += 1
    else:
        print(f"  ❌ code={j.get('code')} msg={j.get('message')}")
except Exception as e:
    print(f"  ❌ ERROR {e}")

print()
print("=" * 60)
print(f" 结果：{passed}/{len(tests_get)+2} 通过")
print("=" * 60)
