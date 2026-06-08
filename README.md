# finetuning-llms-material-didactico-multiformato

Código y datos de los experimentos del TFM *Fine-tuning de modelos de lenguaje para generación controlada de material didáctico multiformato*.

Se parte de un modelo abierto pequeño que cabe en un portátil, se le hace fine-tuning con QLoRA sobre un corpus de material didáctico de fundamentos de programación, y se compara lo que genera el modelo ajustado contra el mismo modelo usado solo con prompting. La comparación va por dos vías, las métricas automáticas de legibilidad y formato, y un juez basado en LLM que puntúa con una rúbrica pedagógica.

El modelo base es `Qwen3-4B-Instruct-2507` cuantizado a 4 bits, en la versión de MLX. Todo está pensado para correr en un Mac con Apple Silicon, porque el entrenamiento y la generación usan `mlx-lm`. En otra plataforma no funciona sin cambios.

## Contenido

```
data/                 corpus en formato chat (system / user / assistant)
  train.jsonl         750 ejemplos de entrenamiento
  valid.jsonl          94 de validación
  test.jsonl           94 de test
  test_annotado.jsonl  el mismo test con metadatos
train/
  configs/qlora.yaml   configuración del fine-tuning con QLoRA
  adapters/            el adapter ya entrenado que sale del proceso
eval/
  generate.py          genera material para prompting y finetuned
  metrics.py           métricas automáticas
  score.py             aplica esas métricas y vuelca un CSV por condición
  prep_judge.py        baraja y anonimiza las generaciones para el juez ciego
  judge_prompt.md      el guion que sigue el juez LLM, con la rúbrica de 7 criterios
  process_judge.py     recoge los veredictos del juez y los pasa a CSV
mapping/              adjuntos del mapping sistemático
requirements.txt
```

El corpus cubre cuatro formatos, explicación, ficha de repaso, pregunta de opción múltiple y ejercicio resuelto, en tres niveles, principiante, intermedio y avanzado. Cada ejemplo lleva un perfil de estudiante en el mensaje de sistema, con su nivel, sus objetivos y los errores que suele cometer, y el modelo tiene que adaptar el material a ese perfil.

## Requisitos

Mac con Apple Silicon y Python 3.11 o superior. Las dependencias se instalan con

```bash
pip install -r requirements.txt
```

Las versiones están fijadas, así que el entorno reproducido es el mismo que se usó en los experimentos.

## Entrenamiento

El fine-tuning se lanza con `mlx-lm` apuntando al config. Descarga el modelo base de Hugging Face la primera vez.

```bash
mlx_lm.lora --config train/configs/qlora.yaml
```

Son 940 iteraciones, QLoRA de rank 16 sobre las últimas 8 capas, con prompt enmascarado para que el modelo solo aprenda de la respuesta. El adapter resultante se guarda en `train/adapters/`. El que viene en el repo es el que se usó para los resultados del TFM, así que se puede evaluar directamente sin volver a entrenar.

## Evaluación

El flujo va en cuatro pasos. Primero se genera el material con las dos condiciones.

```bash
python eval/generate.py --condicion prompting
python eval/generate.py --condicion finetuned
```

`prompting` carga el modelo base tal cual. `finetuned` carga el modelo base más el adapter. Los dos escriben su salida en `eval/results/`.

Después se sacan las métricas automáticas de cada condición.

```bash
python eval/score.py --condicion prompting
python eval/score.py --condicion finetuned
```

Esto mide legibilidad con Fernández-Huerta e INFLESZ, solapamiento con la referencia mediante ROUGE-L en explicaciones y fichas, si las preguntas de opción múltiple están bien formadas, y si el código de los ejercicios resueltos ejecuta sin errores.

Para la parte cualitativa se preparan los items para el juez. El script baraja las generaciones de ambas condiciones y las anonimiza, de forma que el juez puntúa a ciegas sin saber de dónde viene cada material.

```bash
python eval/prep_judge.py
```

Eso deja un fichero por item y un mapa que guarda a qué condición pertenece cada uno. Esos items se pasan a un LLM con el guion de `judge_prompt.md`, que devuelve siete notas de 1 a 4 por material. Una vez recogido el JSON con los veredictos, se procesa.

```bash
python eval/process_judge.py ruta/al/json/del/juez
```

Arroja un CSV por condición y un resumen por criterio y por formato en la terminal.

## Mapping sistemático

La carpeta `mapping/` reúne los adjuntos del mapping sistemático que sustenta el estado del arte del TFM, con las exportaciones de búsqueda de Scopus y Web of Science, las decisiones de cribado y elegibilidad por registro, y la hoja de extracción de los 68 estudios incluidos. El protocolo completo, con las preguntas de investigación, el marco PICOC, los criterios y el flujo PRISMA, está en el Anexo A de la memoria. En `mapping/README.md` se detalla cada fichero.
