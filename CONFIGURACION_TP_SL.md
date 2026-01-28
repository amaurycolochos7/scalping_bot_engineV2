# Configuración de Take Profit y Stop Loss

## 📊 Configuración Actual

### LONG (Compra) 🟢
- **Stop Loss (SL)**: -5% del precio de entrada
  - Precio SL = Precio Entrada × 0.95 (95%)
  - Ejemplo: Entrada a $100 → SL en $95

- **Take Profit (TP)**: +10% del precio de entrada
  - Precio TP = Precio Entrada × 1.10 (110%)
  - Ejemplo: Entrada a $100 → TP en $110

### SHORT (Venta) 🔴
- **Stop Loss (SL)**: +5% del precio de entrada
  - Precio SL = Precio Entrada × 1.05 (105%)
  - Ejemplo: Entrada a $100 → SL en $105

- **Take Profit (TP)**: -10% del precio de entrada
  - Precio TP = Precio Entrada × 0.90 (90%)
  - Ejemplo: Entrada a $100 → TP en $90

## ⚙️ Modificar Configuración

Para ajustar estos valores, edita el archivo `.env`:

```env
TP_PERCENTAGE=10  # Cambia este número para ajustar TP
SL_PERCENTAGE=5   # Cambia este número para ajustar SL
```

## 💡 Ejemplo de Señal

### LONG en BTCUSDT a $45,000
```
Moneda: BTCUSDT
Precio Entrada: $45,000
Take Profit: $49,500 (+10%)
Stop Loss: $42,750 (-5%)
```

### SHORT en ETHUSDT a $2,500
```
Moneda: ETHUSDT
Precio Entrada: $2,500
Take Profit: $2,250 (-10%)
Stop Loss: $2,625 (+5%)
```

## 📈 Risk/Reward Ratio
- **Relación R:R = 2:1** (ganas el doble de lo que arriesgas)
- Si arriesgas 5%, puedes ganar 10%
- Sistema favorable para trading sistemático
