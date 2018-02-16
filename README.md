# python-j2render

Render set of Jinja2 templates for different targets.


Any directory with jinja templates represents a single resource.

For example it might be folder `spring` with two files:

```
spring
  ├── application.yml.j2
  └── env.rc.j2
```
where `application.yml.j2` is: 

```
server:
  port: {{ item.port }}
```
and `env.rc.j2` contains:

```
JAVA_OPTS="-Xms{{ item.xms }}"

```

Now we want to render these templates, using parameters which are stored in a fancy parameter tree:

```
─ targets
  ├── _default
  │   ├── _global.yaml
  │   └── resourceA
  │       ├── _common.yaml
  │       ├── itemA1.yaml
  │       └── itemA2.yaml
  ├── targetX
  │   ├── _global.yaml
  │   └── resourceA
  │       ├── _common.yaml
  │       └── itemA2.yaml
  └── targetY
      ├── _global.yaml
      ├── resourceA
      │   ├── _common.yaml
      │   └── itemA1.yaml
      └── resourceB
          ├── _common.yaml
          └── itemB1.yaml
```

For every triple `(ITEM, RESOURCE, TARGET)` we create two dictionaries and pass them to each template:

* `target` dictionary is a combination of:
    - `_default/_global.yaml`
    - `TARGET/_global.yaml`

  Parameter set in the TARGET/_global.yaml has a precedence over the default value.

* `item` dictionary is a combination of five different dictionaries:
    - `_default/RESOURCE/_common`
    - `TARGET/RESOURCE/_common`
    - `_default/RESOURCE/ITEM`
    - `TARGET/RESOURCE/ITEM`
    - system dictionary
    
    System dictionary is made from environment variables which start with the prefix 'J2RENDER_'. For each variable we
    remove the prefix and add variable to the dictionary. The `J2RENDER_parameter` becomes `parameter` and so on.
    
Now in the output we will get the same directory structure as resource tree has, but with templates rendered with the
collected variables.

## Example

Assume we have the following file tree, and in every yaml file value of the `parameter` is defined differently:

```
─ targets
  ├── _default
  │   ├── _global.yaml        -> parameter: /_default/global
  │   └── my_resource
  │       ├── _common.yaml    -> parameter: /_default/my_resource/common
  │       ├── itemA.yaml      -> parameter: /_default/my_resource/itemA
  │       └── itemB.yaml      -> parameter: /_default/my_resource/itemB
  └── prod
      ├── _global.yaml        -> parameter: /prod/global
      └── my_resource
          ├── _common.yaml    -> parameter: /prod/my_resource/common
          └── itemA.yaml      -> parameter: /prod/my_resource/itemA

```

Lets try to render the following template `resources/my_resource/file.j2`:

```

Target/Default Parameter: {{ target.parameter }}
System/Item/Resource Parameter: {{ item.parameter }}

```

Rendering depends on the target and item.

1. Target: `prod`, item: `itemA`.

    ```
    $ j2render -R my_resource -T prod -I itemA
    $ cat _output/my_resource/itemA/file
    
    Target/Default Parameter: /prod/global
    System/Item/Resource Parameter: /prod/my_resource/itemA
    ```

2. Target: `prod`, item: `itemB` - default parameter fro itemB takes precedence over the common parameter in
   `prod/my_resource/_common.yaml`.

    ```
    $ j2render -R my_resource -T prod -I itemB
    $ cat _output/my_resource/itemB/file 

    Target/Default Parameter: /prod/global
    System/Item/Resource Parameter: /_default/my_resource/itemB
    ```

3. Target: `prod`, item: `itemC` - no item overrides.

    ```
    $ j2render -R my_resource -T prod -I itemC
    $ cat _output/my_resource/itemC/file
    
    Target/Default Parameter: /prod/global
    System/Item/Resource Parameter: /prod/my_resource/common
    ```

4. Target: `dev`, item: `itemA` - no target overrides.

    ```
    $ j2render -R my_resource -T dev -I itemA
    $ cat _output/my_resource/itemA/file 

    Target/Default Parameter: /_default/global
    System/Item/Resource Parameter: /_default/my_resource/itemA
    ```

5. Target: `prod`, item `itemA`, environment variable takes over.

    ```
    $ J2RENDER_parameter=cli j2render -R my_resource -T prod -I itemA
    $ cat _output/my_resource/itemA/file

    Target/Default Parameter: /prod/global
    System/Item/Resource Parameter: cli
    ```
