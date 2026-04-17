# 03 — Seguridad básica (`ir.model.access.csv`)

Sin al menos un permiso, un modelo nuevo es **invisible** para cualquier
usuario distinto del superadmin. Se obtiene un error del tipo
*“You are not allowed to access ‘Mi Modelo’ (mi.modelo)”*.

## Archivo mínimo

```
# security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_mi_modelo_user,mi.modelo user,model_mi_modelo,base.group_user,1,1,1,1
```

Un registro = una fila. Los campos son:

| Columna | Qué es |
|---|---|
| `id` | External ID único. Convención: `access_<modelo>_<grupo>`. |
| `name` | Texto libre (aparece en la interfaz de permisos). |
| `model_id:id` | `model_` + el `_name` del modelo con `.` cambiados por `_`. Ejemplo: `mi.modelo` → `model_mi_modelo`. |
| `group_id:id` | External ID del grupo al que aplica. Vacío = aplica a todos. |
| `perm_read` | Puede listar/ver registros (0/1). |
| `perm_write` | Puede modificar registros. |
| `perm_create` | Puede crear registros. |
| `perm_unlink` | Puede eliminar registros. |

## Plantilla con varios modelos y varios grupos

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
# Usuarios internos: acceso total
access_mi_modelo_user,mi.modelo user,model_mi_modelo,base.group_user,1,1,1,1
access_otro_modelo_user,otro.modelo user,model_otro_modelo,base.group_user,1,1,1,1

# Usuarios del portal: solo lectura
access_mi_modelo_portal,mi.modelo portal,model_mi_modelo,base.group_portal,1,0,0,0

# Modelo “inmutable” (no se pueden eliminar registros)
access_historial_user,historial user,model_historial,base.group_user,1,1,1,0
```

## Grupos más usados

| External ID | Quién entra ahí |
|---|---|
| `base.group_user` | Todos los usuarios internos (empleados). |
| `base.group_portal` | Usuarios del portal (clientes externos). |
| `base.group_public` | Visitante anónimo (raramente se usa aquí). |
| `base.group_system` | Administradores. |

## Checklist cuando añades un modelo nuevo

1. Abre `security/ir.model.access.csv`.
2. Copia una línea existente.
3. Cambia el `id` y el `model_id:id` por los de tu modelo nuevo.
4. Ajusta los permisos (lo normal es `1,1,1,1` para `group_user`).
5. Asegúrate de que el CSV está listado en `data` del `__manifest__.py`
   **antes** que las vistas (siempre primero seguridad).
6. Reinicia con `-u mi_modulo`.

## Reglas de registro (`ir.rule`)

`ir.model.access.csv` es un todo o nada *por modelo y por grupo*. Si
necesitas que un usuario solo vea **sus** registros, se usan reglas
(`ir.rule`) con un `domain`. Eso ya es más avanzado y normalmente se
define en un XML dentro de `security/`.
