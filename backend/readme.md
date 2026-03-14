# SunSmart Backend — API Documentation

## 目录
- [快速启动](#快速启动)
- [项目结构](#项目结构)
- [接口文档](#接口文档)
- [前端接入指南](#前端接入指南)
- [缓存说明](#缓存说明)
- [数据字典](#数据字典)

---

## 快速启动

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动服务

```bash
uvicorn main:app --reload --port 8000
```

启动成功后终端会显示：

```
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO: Started reloader process
```

### 3. 查看接口文档

浏览器打开 [http://localhost:8000/docs](http://localhost:8000/docs)，可以在线测试所有接口。

---

## 项目结构

```
backend/
├── main.py              # FastAPI 入口，CORS 配置
├── routers/
│   └── uv.py            # UV 相关路由定义
├── services/
│   └── uv_service.py    # 业务逻辑：调外部 API、计算烧伤时间、缓存
├── models/
│   └── uv_model.py      # Pydantic 数据模型
└── requirements.txt
```

---

## 接口文档

### GET `/api/uv/current`

获取当前位置的实时 UV 数据，包括 UV 指数、危险等级、皮肤烧伤倒计时、每小时预报。

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `lat` | float | ✅ | 纬度，例如 `-37.8136` |
| `lon` | float | ✅ | 经度，例如 `144.9631` |
| `skin_type` | string | ❌ | 肤色类型，默认 `type2`，见下方说明 |

**`skin_type` 可选值**

| 值 | 说明 | MED 值 |
|----|------|--------|
| `type1` | 非常白皙，容易晒伤 | 200 |
| `type2` | 白皙（默认） | 250 |
| `type3` | 中等肤色 | 300 |
| `type4` | 偏深肤色 | 450 |

**请求示例**

```
GET http://localhost:8000/api/uv/current?lat=-37.8136&lon=144.9631&skin_type=type2
```

**成功响应 `200 OK`**

```json
{
  "uv_index": 8.0,
  "level": "Very High",
  "level_color": "#f87171",
  "burn_time_minutes": 12,
  "alert_message": "Your skin will start burning in ~12 minutes — find shade or apply SPF 50+ now.",
  "spf_recommendation": "SPF 50+",
  "hourly_forecast": [
    {
      "time": "7:00",
      "uv_index": 2.1,
      "level": "Low",
      "color": "#4ade80",
      "is_current": false
    },
    {
      "time": "13:00",
      "uv_index": 8.0,
      "level": "Very High",
      "color": "#f87171",
      "is_current": true
    }
  ]
}
```

**错误响应**

| 状态码 | 原因 |
|--------|------|
| `422` | 参数缺失或格式错误（lat/lon 不是数字）|
| `500` | 调用 Open-Meteo 超时或失败 |

---

## 前端接入指南

### Vue 推荐写法

新建 `composables/useUVData.js`，统一管理 UV 数据请求和缓存：

```javascript
import { ref } from 'vue'

const uvData = ref(null)
const lastFetched = ref(null)
const CACHE_TTL = 5 * 60 * 1000  // 前端缓存 5 分钟

export function useUVData() {

  async function loadUVData(skinType = 'type2') {
    // 1. 优先用内存缓存（切换页面时直接复用，无需重新请求）
    if (uvData.value && Date.now() - lastFetched.value < CACHE_TTL) {
      return uvData.value
    }

    // 2. 次选 sessionStorage（刷新页面后仍可复用）
    const stored = sessionStorage.getItem('uv_cache')
    if (stored) {
      const parsed = JSON.parse(stored)
      if (Date.now() - parsed.timestamp < CACHE_TTL) {
        uvData.value = parsed.data
        lastFetched.value = parsed.timestamp
        return uvData.value
      }
    }

    // 3. 缓存过期或首次访问 — 获取 GPS 并请求后端
    const pos = await getGPSPosition()
    const res = await fetch(
      `http://localhost:8000/api/uv/current?lat=${pos.lat}&lon=${pos.lon}&skin_type=${skinType}`
    )
    const data = await res.json()

    // 存入内存和 sessionStorage
    uvData.value = data
    lastFetched.value = Date.now()
    sessionStorage.setItem('uv_cache', JSON.stringify({
      timestamp: lastFetched.value,
      data
    }))

    return data
  }

  function getGPSPosition() {
    return new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(
        (pos) => resolve({
          lat: pos.coords.latitude,
          lon: pos.coords.longitude
        }),
        (err) => reject(err)
      )
    })
  }

  return { uvData, loadUVData }
}
```

### 在组件里使用

```vue
<script setup>
import { onMounted } from 'vue'
import { useUVData } from '@/composables/useUVData'

const { uvData, loadUVData } = useUVData()

onMounted(async () => {
  await loadUVData()
  // uvData.value 现在包含所有 UV 数据，直接绑定到模板
})
</script>

<template>
  <div v-if="uvData">
    <p>UV Index: {{ uvData.uv_index }}</p>
    <p>{{ uvData.alert_message }}</p>
    <p>Burn time: {{ uvData.burn_time_minutes }} min</p>
  </div>
</template>
```

### 跨域说明

后端已配置 CORS，允许 `localhost:5173`（Vue 默认端口）访问，开发阶段无需任何额外配置。

如果你的 Vue dev server 跑在其他端口，告知后端同学在 `main.py` 的 `allow_origins` 里添加对应端口。

---

## 缓存说明

请求流程如下，正常情况下 GPS 弹窗只出现一次：

```
用户切换页面
    ↓
Vue 内存缓存还有效？ → 直接用，0 网络请求
    ↓ 否
sessionStorage 缓存还有效？ → 直接用，0 网络请求
    ↓ 否
请求 GET /api/uv/current
    ↓
后端内存缓存命中？ → 不调 Open-Meteo，直接返回
    ↓ 否
调用 Open-Meteo API，存缓存，返回数据
```

| 缓存层 | 有效期 | 说明 |
|--------|--------|------|
| Vue 内存（ref） | 5 分钟 | 页面切换时复用 |
| sessionStorage | 5 分钟 | 页面刷新后复用 |
| 后端内存（dict） | 15 分钟 | 相同坐标不重复调 Open-Meteo |

---

## 数据字典

### UV 等级对照

| UV Index | 等级 | 颜色（`level_color`） | 推荐 SPF |
|----------|------|----------------------|---------|
| 0 – 2 | Low | `#4ade80` | SPF 15+ |
| 3 – 5 | Moderate | `#facc15` | SPF 30+ |
| 6 – 7 | High | `#fb923c` | SPF 30+ |
| 8 – 10 | Very High | `#f87171` | SPF 50+ |
| 11+ | Extreme | `#c084fc` | SPF 50+ |

### `hourly_forecast` 数组说明

每个元素代表当天 6:00–20:00 中的一个小时：

| 字段 | 类型 | 说明 |
|------|------|------|
| `time` | string | 时间，如 `"13:00"` |
| `uv_index` | float | 该小时 UV 指数 |
| `level` | string | 等级文字 |
| `color` | string | 对应颜色 hex |
| `is_current` | boolean | 是否为当前小时，用于高亮 |