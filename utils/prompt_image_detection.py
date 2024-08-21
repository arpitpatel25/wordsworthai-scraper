prompt = """I  want you to detect following thins on an image provided.

You should detect if the image has a human. The human may not be full, like they me be partial in the image. True or False

You should detect if the image has a product, or an object. True or False

You should detect if the image has multiple products (they should be sloghlty diffet from one anothr. just slightly to be categorixes as diffenet and hence multiple/). True or False

Finally you should respond only in following way::

True, False, False

True, True, False.
This is, dont write anything except True or False for each case. The first will be about human detection, decond will be object detection, third will be multiple object detection. 
"""
