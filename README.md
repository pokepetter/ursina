# ursina ʕ •ᴥ•ʔゝ□
A game engine built on panda3d and python.  

To download and install:

    $ pip install git+https://github.com/pokepetter/ursina.git

If you want to easily edit the source, it's recommended to clone the git repo and  install as develop.

Dependencies:
  * python 3.6+
  * panda3d
  * screeninfo
  * pillow and psd-tools, if you want .psd compression.

----  

        application
            append_path()

        build -project_folder   # packaging tool. puts all dependancies into a folder so you can distribute your application

        camera(Entity)
            orthographic
            fov
            aspect_ratio

        color
            color(h, s, v, a=1)
            rgba(r, g, b, a=1)
            to_hsv(color)
            inverse(color)
            random_color()
            tint(color, amount=.2)

            white
            smoke
            light_gray
            gray
            dark_gray
            black
            red
            orange
            yellow
            lime
            green
            turquoise =     color(150, 1, 1)
            cyan
            azure
            blue
            violet
            magenta
            pink
            clear
            white33
            white50
            white66
            black33
            black50
            black66
            text = smoke
            panda_background = dark_gray
            panda_button = black66
            panda_text = smoke
            light_text = smoke
            dark_text = color(0, 0, .1)
            text_color = light_text

        Entity
            name    # defaults to class name
            type    # returns class name as string
            enabled
            parent
            collision
            collider    # only 'box' supported for now. automatically fits model bounds
            hovered

            model
            color
            texture
            texture_scale, texture_offset
            render_queue

            position
            origin
            x, y, z
            world_position
            world_x, world_y, world_z
            rotation
            rotation_x, rotation_y, rotation_z
            scale
            scale_x, scale_y, sale_z
            world_scale
            world_scale_x, world_scale_y, worl_scale_z
            forward, back, right, left, up, down

            reparent_to(entity)     # keeps position, rotation and scale relative to world space
            add_script('script_name')
            remove_script('script_name')

            look_at(Vec3 or Entity)
            has_ansestor()
            children()

            animate_position()
            animate_scale()
            shake(duration=.2, magnitude=1, speed=.05)
            animate_color()

            # these functions gets automatically called if they exsist:
                start(self)
                input(self, key)
                update(self, dt)
                on_mouse_enter(self)
                on_mouse_exit(self)
                on_click(self)
                on_destroy(self)

        input
            held_keys   # dict that hold key states.

        internal_prefabs
            Animation(Entity)   # for 2D animations
            Button
            Cursor
            Draggable   # for easy drag and drop
            Grid(w, h, thickness)
            Mesh(verts, tris=None, colors=None, uvs=None, normals=None, static=True, mode='triangle', thickness=1)
                modes
                    'triangle'
                    'tristrip'
                    'ngon'
                    'line'
                    'lines'
                    'point'
                thickness
            Plane
            Sky
            Sprite  # scales to fit texture dimensions
            Text
                text
                font
                line_height
                width
                height
                wordwrap
                align
                    'left', 'center', 'right'
                    
                # supports inline scale and color tags:
                # example_text = Text('<scale:1.5><orange>Title \n<scale:1>Increase <red>max health <default>with 25%.')
            Tooltip

        mouse
            enabled
            locked      # lock to center of screen for first person controller and such
            position
            x, y
            delta
            delta_drag
            velocity
            double_click_distance = .5      # in seconds
            left, right, middle
            
            normal
            point
            collision
                collided
                entity
                position
                normal
                
        pandamath
            distance(entity_a, entity_b)
            lerp(a, b, t)
            inverselerp(a, b, t)
            clamp(value, floor, ceiling)
            chunk_list(l, chunk_size)   # yield successive chunks from list
        
        
        
        pandastuff
            invoke(function, *args, **kwargs)
            destroy(entity, delay=0)
            compress_textures(name=None)
            
        raycaster
            raycast(self, origin, direction, dist=1000, traverse_target=None, debug=False) # returns Hit
            Hit
                hit
                entity
                distance
                point
                
        scene
            camera
            ui
            
        useful
            camel_to_snake(value)
            snake_to_camel(value)
            multireplace(string, replacements, ignore_case=False)
            printvar(var)
            
        window
            center_on_screen
            size
            position
            fullscreen
            color       # clear color / background
            fps_counter
            exit_button
            


