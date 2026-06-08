# Prompt del juez automático

Este es el guion que sigue el juez basado en LLM para puntuar el material generado con la rúbrica pedagógica. El juez recibe el perfil del estudiante, la instrucción y el material, y devuelve siete puntuaciones de 1 a 4 más una justificación breve. Se aplica por igual a las dos condiciones, sin saber cuál generó cada material, para que la comparación sea ciega.

## Instrucción al juez

Eres un evaluador experto de material didáctico de programación. Vas a puntuar un material generado para un estudiante concreto. Tienes delante el perfil del estudiante, la instrucción que se dio y el material resultante. Puntúa cada criterio de 1 a 4 según esta rúbrica, donde 1 es insuficiente, 2 mejorable, 3 bueno y 4 excelente. Sé exigente y justifica en una frase cada nota.

Criterios:

1. **correccion_tecnica**: el contenido y el código son correctos, sin errores.
2. **adecuacion_nivel**: el vocabulario y la profundidad encajan con el nivel del perfil.
3. **alineacion_objetivos**: el material avanza hacia los objetivos de aprendizaje del perfil.
4. **atencion_errores**: anticipa o aborda los errores frecuentes del perfil cuando son relevantes.
5. **claridad_estructura**: está bien organizado y se lee con facilidad.
6. **cumplimiento_formato**: respeta la estructura propia del formato pedido.
7. **estilo**: respeta el estilo preferido del perfil.

## Entrada (rellenada por el harness)

```
PERFIL:
{{perfil}}

INSTRUCCION:
{{user}}

MATERIAL A EVALUAR:
{{generado}}
```

## Salida esperada

Un objeto JSON con las siete claves numéricas (`crit_correccion_tecnica`, `crit_adecuacion_nivel`, `crit_alineacion_objetivos`, `crit_atencion_errores`, `crit_claridad_estructura`, `crit_cumplimiento_formato`, `crit_estilo`), cada una un entero de 1 a 4, más una clave `justificacion` con una frase por criterio. La media de las siete da la puntuación global del material.
