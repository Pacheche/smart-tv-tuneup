# Material de terceros

Código copiado de otros proyectos, con su origen y licencia.

## cleanyourtv — regexes del núcleo de Android

- **Qué:** las constantes `CORE_RE` y `CORE_OK` de `scripts/plan_android.py` están
  copiadas **literales**, incluida la anotación de origen en el comentario.
- **Origen:** [Gathin23/cleanyourtv](https://github.com/Gathin23/cleanyourtv),
  archivo `tools/disable.sh`, líneas 68-69, commit fijo
  `6e8615eb0be0e843ceeebedae246d69f3e0a88d7` (verificado con `git rev-parse HEAD`).
- **Licencia:** MIT, Copyright (c) 2026 Gathin.
- **Por qué importa:** es la única parte donde el criterio de "qué es núcleo" no es
  mío; si cleanyourtv corrige sus regexes, hay que volver a verificarlas contra ese
  commit antes de cambiarlas acá.

## free-my-tv — patrón de menús de fábrica

- **Qué:** `FACTORY_RE` de `scripts/plan_android.py`, tomado del patrón `FACTORY`.
- **Origen:** [simbasjungles/free-my-tv](https://github.com/simbasjungles/free-my-tv),
  archivo `app/src/io/freemytv/HomeMode.java`.
- **Licencia:** MIT, Copyright (c) 2026 Free My TV contributors.

El texto completo de cada licencia MIT está en el archivo LICENSE de su repositorio.
