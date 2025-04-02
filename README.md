# DP32-asm

**Хреновый ассемблер дла процессора DP32**

## Установка

С недавних пор я обновил структуру проекта таким образом, чтобы ее можно было установить через pip и при этом не схлопотать конфликтов с остальными питоновскими пакетами. Самый простой вариант установки - использование pip. Вы можете стянуть этот репозиторий и в корневой дирректории выполнить:

```bash
pip install .
```

После чего вызывать ассемблер можно будет командой dp32asm

## Использование

На вход ассемблер принимает текстовые файлы а на выходе создает файлы в двух форматах - .bin и .lab. Первый - сырые байты программы, записанные в файл, второй - в формате, который можно вставить в VHDL для использования в лабораторной работе

Для испльзования необходимо запустить программу main.py. Для получения короткой справки можно передать флаг `-h`. Поскольку этот ридмишник я пишу поздно, пока ограничусь этим

Схема использования:

```bash
dp32asm <source-file> -f <lab/bin> -o <output-file-name>
```

### Генерация отладочной информации

В ассемблере встроена возможность генерации отладочной информации. Она добавлена для дебаггера, который в фиговом виде вы сможете найти на https://git.inkling.su/ElectronixTM/dp32-proto.git. Он сырой и нужен был по долгу службы. Опирается на программную эмуляцию процессора DP32, поэтому не дает гарантий, что отдебаженный на ней код будет работать на реальном VHDL проекте. Но если отчаялись - дерзайте.

Чтобы сгенерировать отладочный файл (по умолчанию dbg.json), достаточно передать флаг -d. Если хочется заодно указать, в какой файл отладочную информацию сложить - можно передать параметр --debug-file

```
dp32asm <source-file> -o <output-file-name> -d --debug-file <debug-file-name>
```

## Описание синтаксиса ассемблера

В общем случае ассемблеру не важно расширение файла, но вам могут понравится `.dpasm` и `.dasm`. Сам язык ассемблера построен на основе методического пособия к лабораторной работе и содержит все команды от туда, однако записываются они немного в другой форме. Также ассемблер старается взять на себя сложности махинаций с размером операндов, поэтому инструкции, отличающиеся только размерами операндов проходят под одной и той же мнемоникой. Тем не менее порядок операндов должен строго соответсвовать порядку в методичке

Список мнемоник ассемблера таков:

- `add` - сложение r3 <- r1 + r2 или r3 <- r1 + i8
- `sub` - вычитание r3 <- r1 - r2 или r3 <- r1 - i8
- `mul` - умножение r3 <- r1 * r2 или r3 <- r1 * i8
- `div` - целочисленное деление r3 <- r1 / r2 или r3 <- r1 / i8
- `and` - побитовое И r3 <- r1 & r2
- `or` - побитовое ИЛИ r3 <- r1 | r2
- `xor` - побитовое исключающее ИЛИ r3 <- r1 ^ r2
- `mask` - побитовая маска r3 <- r1 & !r2, где `!` - инверсия
- `load` - загрузка из памяти r3 <- M[r1 + disp32] или r3 <- M[r1 + disp8]
- `store` - загрузка из памяти M[r1 + disp32] <- r3 или M[r1 + disp8] <- r3
- `branch` - команда условного перехода. Переход PC <- r1 + i8/i32 или PC <- PC + i8/i32 совершается на основе содержимого регистра флагов, который соотвествует следующй форме `условие = ((V&v)|(N&n)|(Z&z))==i`, при этом i задается произвольно. Для удобства пользования ассемблером эти условия можно задать конструкцией в фигурных скобках {i=1VNZ}. Порядок флагов важен (сложно иначе парсить регулярками), регистр - нет. Присутствие буквы переведется в 1, отсутствие в 0
- `db`, `dh`, `dw` - диррективы резервирования памяти - 8 бит, 16 бит и 32 бита соотвественно. Все они не являются командами процессору и просто заполняют кусок памяти указанными числами. Все эти команды держат выравнивание и *заполняют строку слева направо*, все, что требуется довыровнять забивается нулями. Положить сюда вы можете все, что ассемблер распознает как число, а именно: числовые литераллы, все, что через `#define` переводится в число, имена меток (он вобьет указатель на них), относительные метки (Стоит учитывать, что их расположение считается относительно их конца. То есть положенное число может на единицу отличаться от того, что вы ожидаете), даже условия `{i=2vz}`, поскольку это синтаксический сахар, заменяющий собой числа

Для упрощения навигации по памяти вводятся метки. Фактически на этапе ассемблирования все метки превратятся в числа. На данный момент в реализации ассемблера метка считается 32битным числом не зависимо от того, какое фактически число в ней лежит. Будьте внимательны с этим, так как это может создавать не оптимизированный или нежелательный код. Метка вводится как `label1:`, а затем к ней можно обращаться просто по имени, как `label1`

Пример программы:

```
loop:
add r3 r1 r2
sub r3 r3 r2
sub r3 r3 r1
branch {i=1z} rel loop
```

Ключевое слово `rel` указывает на то, что в этом конкретном месте нужно вставить не абсолютный адрес метки, а смещение до нее (оно может быть как положительное, так и отрицательное). Даже если смещение мало, оно все еще считается 32 битным числом - не забывайте об этом.

## Типы операндов

1. Регистры - находятся в диапазоне `r0` - `r255`
2. Числа - то, что вы пишете напрямую: -6, 12. При этом метки тоже считаются числами, только они априорно 32 битные независимо от их фактического содержимого
3. Условия - синтаксический сахар, позволяющий читаемо записать условия в необходимом для процессора виде. Пример может выглядеть так: `{i=1VZ}` - проверяет, стоит ли флаг oVerflow или Zero в единице
4. Память - фактически очень любопытная штука, так как только в ней можно задействовать возможности процессора по адресации. Используются в основном для команд работы с памятью и необходимы в условном ветвлении с применением регистров. Пишутся в квадратных скобках: `[r27 + 1024]`. Также можно использовать имена меток, если команда позволяет 32 битные числа: `[r21 + x]`. Кстати плюс здесь не обязателен и ставится только для красоты, а вот порядок операндов важен, сначала идет регистр, потом число. Внутри скобок также работает `rel`: `[r22 + rel main]`

## 2 команды препроцессору

В ассемблере на данный момент есть всего 2 команды препроцессору - `#define` и `#undefine`. Нужны они по большей части чтобы заводить поименованные константы. Применение просто как 5 копеек

```
#define x 12

arg: db x 13 x 13

#undefine x
```

Замечу, что в отличие от Сишного define, этот всегда требует 2 аргумента - что заменять и на что заменять. Работает чуть ли не как обычная замена регулярными выражениями (лишь чуть сложнее)

Функциональность этих 2 команд я почти не тестировал, поэтому буду рад, если поделитесь замечаниями, которые возникнут в процессе вашей работы

## Отладка

Если передать ассемблеру флаг -d, то вместе с файлом бинаря/лабы он сгенерирует файл с отладочной информацией. По умолчанию он называется dbg.json, который будет содержать информацию об адресах меток, а также о том, какая инструкция лежит по какому адресу. В человеку читать ее не надо, нужен для отладчика, который я пишу (если кому нужен - выложу)

Формат файла отладки:

```json
{
    "src": "absolute/path/to/source"
    "labels" : {
        "label1": 1
        "label2": 2
        ...
    },
    "instructions" : {
        "<offset-in-words>" : {
        "lenght": 2,
        "srcline": 3
        }
        ...
    }
}
```

## Пояснение к ошибкам

Поддержка ошибок сделана не очень приятно для пользователя, потому что ассемблер не считает своим долгом выдавать диагностику неисправности. В основном он просто укажет на то место, с которого у него что-то пошло не так. В связи с этим для упрощения отладки (которая видимо больше умозрительная) я поясню по поводу некоторых сообщений

### Ошибки лексера

Он подчеркнет символы, на которых у него что-то отъехало. В связи с этим прошу заметить, что лексер не будет смотреть на дифайны, они нужны только для того, чтобы заменить то, что может быть именами меток, то есть для создания поименованных констант

### Ошибки парсера

Поскольку парсер не особенно в курсе, где он там находится в контексте исходного кода и кушает только выход лексера (токены), поэтому он просто укажет вам строку с символом, с которым у него не заладилось и выдаст его тип

### Ошибки ассемблирования

Бывают разные, но фактически могут разбиться об использование разных вещей вроде несуществующих меток или использование направильных размеров операндов. Последнее поясню:

Когда вы пытаетесь засунуть в 8 битное поле число, которое туда поместиться не может (а могут только -128 -> 127), вам не скажет, что вы по размерам сломались, вам скажет, что типы операндов не сходятся. Дело в том, что ассемблер изо всех сил старается сделать то, что вы ему написали и если вы пытаетесь в 8 битное поле затолкать 277, то он попытается как-то привести это число к какому-то типу и ему останется только решить, что это 32-битное поле. Но для арифметики например 32битное поле не задействуется нигде, поэтому он упадет именно по типам операндов, а не по переполнениям
