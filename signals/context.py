"""
Contexto educativo por señal: qué es, tesis económica, lectura del valor actual.
Se usa en las vistas para mostrar explicaciones junto a los gráficos.
"""

# Cada entrada: { "que_es", "tesis", "direccion", "que_vigilar" }
SIGNAL_CONTEXT = {

    "SPREAD_US_DE": {
        "que_es": "Diferencial entre el Treasury 10Y de EEUU y el Bund 10Y alemán (en puntos porcentuales).",
        "tesis": (
            "Los inversores globales eligen entre treasuries y bunds. "
            "Cuando EEUU paga más que Alemania, el capital fluye hacia dólares para comprar treasuries → DXY sube, EUR/USD baja. "
            "La correlación histórica con EUR/USD es ~0.70-0.85."
        ),
        "direccion": "Spread se amplía → DXY ↑ EUR/USD ↓ | Spread se achica → DXY ↓ EUR/USD ↑",
        "que_vigilar": (
            "Movimientos > 10bps en una sesión son significativos. "
            "Si el spread sube pero el DXY no reacciona → imbalance potencial (ver correlación rolling). "
            "El spread US-DE fue el principal driver de EUR/USD en 2022 cuando la Fed subió agresivo y el BCE demoró."
        ),
    },

    "SPREAD_US_JP": {
        "que_es": "Diferencial entre el Treasury 10Y de EEUU y el JGB 10Y japonés.",
        "tesis": (
            "Japón históricamente tiene yields ultra-bajas. Los fondos tomaban yen prestado barato y compraban treasuries "
            "(carry trade). Cuando el diferencial se achica → el carry pierde atractivo → posiciones se cierran → "
            "yen se aprecia violentamente. Asimetría clave: el carry se arma lento y se deshace rápido."
        ),
        "direccion": "Spread amplio → USD/JPY ↑ (yen débil, carry activo) | Spread cae → USD/JPY ↓ (carry se desarma)",
        "que_vigilar": (
            "Cualquier movimiento del BOJ (cambios en YCC/control de curva) puede colapsar el spread de golpe. "
            "El episodio de agosto 2024: el BOJ subió tasas → JP10Y subió → spread cayó → USD/JPY perdió 10 figuras en días. "
            "Con datos de Fase 1 (FRED lag mensual) esta señal es rezagada — se mejora en Fase 8 con tvdatafeed."
        ),
    },

    "CURVE_2_10": {
        "que_es": "Diferencial Treasury 10Y menos Treasury 2Y. La forma de la curva de rendimientos más seguida.",
        "tesis": (
            "La Fed controla el corto plazo (2Y). El mercado fija el largo (10Y) según expectativas de crecimiento e inflación. "
            "Cuando la Fed sube agresivo, el 2Y sube más que el 10Y → inversión. "
            "La inversión indica que el mercado anticipa recesión futura + recortes de tasas."
        ),
        "direccion": (
            "Positivo (normal): crecimiento esperado. "
            "Cerca de 0 (plana): transición/incertidumbre. "
            "Negativo (invertida): mercado anticipa recesión."
        ),
        "que_vigilar": (
            "La inversión en sí no es señal de entrada. Es contexto macro. Históricamente precede recesiones "
            "con 12-18 meses de adelanto. Lo más importante: la velocidad de des-inversión. "
            "En 2024 la curva empezó a des-invertirse — no porque mejoró el outlook, sino porque el 2Y cayó "
            "anticipando recortes de Fed."
        ),
    },

    "CURVE_2_5": {
        "que_es": "Diferencial Treasury 5Y menos Treasury 2Y. Tramo corto-medio de la curva.",
        "tesis": (
            "Captura las expectativas de política monetaria en el horizonte de 1-3 años. "
            "Más sensible a cambios en expectativas de la Fed que el 2-10."
        ),
        "direccion": "Invertida en 2-5 antes que 2-10 → la presión de política monetaria es más próxima y aguda.",
        "que_vigilar": (
            "Cuando 2-5 se des-invierte antes que 2-10, el mercado espera recortes en el horizonte próximo "
            "pero no necesariamente ve crecimiento de largo plazo."
        ),
    },

    "CURVE_5_10": {
        "que_es": "Diferencial Treasury 10Y menos Treasury 5Y. Panza larga de la curva.",
        "tesis": (
            "Refleja expectativas de crecimiento e inflación de largo plazo. "
            "Menos afectada por política monetaria, más por fundamentals reales."
        ),
        "direccion": "Positiva: mercado ve crecimiento y/o inflación sostenidos. Negativa: pesimismo estructural.",
        "que_vigilar": (
            "Si 5-10 sube mientras 2-5 está invertida → 'bull steepener' → mercado espera recortes pronto "
            "pero ve inflación estructural. Combinación históricamente compleja para renta fija."
        ),
    },

    "REAL_YIELD": {
        "que_es": "Rendimiento real del Treasury 10Y: nominal menos expectativas de inflación a 10 años (TIPS).",
        "tesis": (
            "El real yield es el costo real del capital. Si es negativo → tener bonos pierde poder adquisitivo "
            "→ el capital busca activos reales (oro, commodities, acciones). "
            "Si sube y se vuelve positivo alto → los bonos tienen sentido → capital sale de growth/oro."
        ),
        "direccion": "Real yield baja/negativo → Oro ↑, Growth ↑ | Real yield sube/positivo → Oro ↓, Value > Growth",
        "que_vigilar": (
            "El cruce de 0 (de positivo a negativo o viceversa) es el evento más relevante. "
            "En 2020-2021 llegó a -1% → oro en máximos históricos ~$2.075. "
            "Cuando la Fed empezó a subir en 2022 y el real yield volvió a +2.5% → oro cayó $400. "
            "Actualmente en zona positiva alta → entorno estructuralmente negativo para gold/growth."
        ),
    },

    "HY": {
        "que_es": "ICE BofA US High Yield OAS: spread de bonos corporativos high yield vs treasury de mismo vencimiento (en %).",
        "tesis": (
            "Mide cuánto extra pagan las empresas más riesgosas vs el gobierno. "
            "Es un indicador líder de risk-off: el crédito corporativo se deteriora ANTES de que las acciones caigan. "
            "Los bonistas ven el riesgo antes que los accionistas."
        ),
        "direccion": "Spread comprime → apetito de riesgo alto | Spread se amplía → deterioro de crédito, precede caídas",
        "que_vigilar": (
            "Rangos: < 2.8% euforia, 2.8-3.8% normal, 3.8-5.0% cauteloso, 5.0-6.5% risk-off, > 6.5% pánico. "
            "Crisis 2008: ~20%. COVID 2020: ~11%. "
            "⚠️ Nota: FRED solo tiene esta serie desde Oct 2023 por cambio de licencia ICE. "
            "Para historia más larga se usa BAA10Y como proxy."
        ),
    },

    "BAA10Y": {
        "que_es": "Moody's Baa Corporate Bond Yield Spread vs 10Y Treasury. Spread de bonos grado inversión (BBB).",
        "tesis": (
            "Proxy de crédito con historia desde 1986. Correlación ~0.87 con HY. "
            "Mide el costo de capital de empresas investment grade. "
            "Sube cuando el mercado percibe más riesgo de crédito o iliquidez."
        ),
        "direccion": "Spread comprime → condiciones de crédito laxas | Spread amplía → stress de crédito",
        "que_vigilar": (
            "Rangos orientativos: < 1.5% muy apretado, 1.5-2.0% normal, 2.0-2.8% cauteloso, "
            "2.8-4.0% risk-off, > 4.0% crisis. COVID 2020: ~4.5%. Crisis 2008: ~6%."
        ),
    },

    "SPREAD_HY_IG": {
        "que_es": "Diferencial entre el spread HY (high yield) y el spread IG (investment grade). Mide la prima por riesgo.",
        "tesis": (
            "Cuando se amplía rápido → el mercado está penalizando más agresivamente el riesgo extra "
            "→ señal de stress de crédito más refinada que el HY solo. "
            "En pánico, los inversores huyen de HY a IG → el diferencial se dispara."
        ),
        "direccion": "Diferencial se amplía → flight to quality dentro del crédito | Comprime → apetito uniforme",
        "que_vigilar": "Ampliación rápida (> 0.5% en semanas) precede deterioro visible en equities.",
    },

    "DXY": {
        "que_es": "US Dollar Index: valor del dólar vs una cesta de 6 divisas principales (EUR 57%, JPY 14%, GBP 12%, otros).",
        "tesis": (
            "El dólar es el activo de refugio global. En risk-off → DXY sube. "
            "También sube cuando los diferenciales de tasas favorecen a EEUU. "
            "DXY alto → presión sobre commodities (precio en USD) y mercados emergentes (deuda en USD más cara)."
        ),
        "direccion": "DXY sube → presión en oro, EM, commodities | DXY baja → favorable para activos de riesgo globales",
        "que_vigilar": (
            "La tendencia de 20 días importa más que el nivel. "
            "DXY subiendo mientras yields EEUU caen → comportamiento de refuge (risk-off puro). "
            "DXY subiendo con yields EEUU subiendo → diferencial de tasas, no miedo."
        ),
    },

    "GOLD": {
        "que_es": "Precio del oro en USD/oz (futuros continuos).",
        "tesis": (
            "El oro no tiene yield. Su precio sube cuando el costo de oportunidad de tenerlo baja "
            "(real yield negativo) o cuando hay incertidumbre sistémica. "
            "También funciona como cobertura de inflación y de riesgo geopolítico."
        ),
        "direccion": "Real yield baja → Oro ↑ | DXY sube → Oro ↓ (presión por denominación en USD)",
        "que_vigilar": (
            "Si el oro sube con real yield alto → hay driver de refugio/geopolítico, no de tasas. "
            "Si el oro cae con real yield negativo → hay presión de liquidez (vendiendo todo para conseguir cash). "
            "Ambas situaciones son señales de alerta."
        ),
    },

    "VIX": {
        "que_es": "CBOE Volatility Index: volatilidad implícita esperada del S&P 500 para los próximos 30 días.",
        "tesis": (
            "El 'índice del miedo'. Sube cuando los operadores compran puts (seguro contra caídas). "
            "No predice dirección, mide incertidumbre y velocidad esperada de movimiento."
        ),
        "direccion": "VIX < 15: calma. 15-20: normal. 20-30: cautela. 30-40: miedo. > 40: pánico",
        "que_vigilar": (
            "VIX alto con mercados cayendo → confirma risk-off. "
            "VIX bajo con mercados en máximos → complacencia, posible setup de reversión. "
            "COVID 2020: VIX llegó a 80. Agosto 2024: llegó a 65 intraday."
        ),
    },

    "SOFR": {
        "que_es": "Secured Overnight Financing Rate: tasa de financiamiento overnight en el mercado de repos de EEUU.",
        "tesis": (
            "Reemplazó al LIBOR como referencia de tasas de corto plazo. "
            "Refleja el costo real de financiamiento overnight de los grandes bancos. "
            "Queda muy cerca de la tasa objetivo de la Fed."
        ),
        "direccion": "SOFR sube → Fed sube/subió tasas | SOFR baja → Fed recorta o mercado anticipa recortes",
        "que_vigilar": (
            "Divergencia entre SOFR y expectativas del mercado (futuros SR3) → "
            "oportunidad de posición en tasas. En Fase 8 se integra SR3 para ver la curva de expectativas completa."
        ),
    },
}

# Context para correlation breakdowns
CORRELATION_CONTEXT = {
    ("SPREAD_US_JP", "DXY"): {
        "tesis": (
            "Normalmente el diferencial US-JP y el DXY se mueven juntos: "
            "mayor diferencial → capital hacia USD → DXY sube. "
            "Cuando se desconectan, uno de los dos está 'equivocado': "
            "o el DXY no ha reaccionado aún al diferencial (DXY va a subir) "
            "o el diferencial cayó pero el DXY todavía no lo refleja (DXY va a bajar)."
        ),
        "implicancia": "El diferencial de tasas es el fundamento. El DXY suele hacer el catch-up.",
    },
    ("REAL10Y", "GOLD"): {
        "tesis": (
            "La correlación inversa real yield / oro es una de las más estables en macro. "
            "Cuando se rompe, hay un factor externo dominando: "
            "compras de bancos centrales, riesgo geopolítico agudo, o stress de liquidez "
            "(venden oro para conseguir cash)."
        ),
        "implicancia": "Si oro sube con real yield alto → hay driver no-tasas activo. Vigilar geopolítica y flows de CB.",
    },
    ("HY", "SPY"): {
        "tesis": (
            "El crédito HY y las acciones miden riesgo desde ángulos distintos pero suelen ir juntos. "
            "Cuando se desconectan: si HY spread sube y acciones no caen → el crédito está viendo riesgo "
            "que las acciones todavía no descontaron (señal bajista para equities). "
            "Si las acciones caen y el HY no se mueve → puede ser corrección técnica sin fundamento crediticio."
        ),
        "implicancia": "El crédito lideriza. Si HY spread sube solo → precaución en equities.",
    },
    ("SPREAD_US_DE", "DXY"): {
        "tesis": (
            "El diferencial US-DE es el fundamento del EUR/USD y por extensión del DXY (EUR es 57% del índice). "
            "Cuando se desconectan, hay flows no-fundamentales dominando: "
            "intervenciones, rebalanceos de cartera, o eventos geopolíticos que afectan flujos hacia Europa."
        ),
        "implicancia": "Desconexión prolongada → oportunidad macro. El diferencial de tasas suele imponerse en semanas.",
    },
}


def get_signal_context(asset: str) -> dict | None:
    return SIGNAL_CONTEXT.get(asset)


def get_corr_context(asset_a: str, asset_b: str) -> dict | None:
    return (
        CORRELATION_CONTEXT.get((asset_a, asset_b)) or
        CORRELATION_CONTEXT.get((asset_b, asset_a))
    )
