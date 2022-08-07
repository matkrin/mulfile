mulfile
=======

Mulfile is a Python library for reading .mul and .flm files, acquired by the
scanning tunneling microscopy (STM) software "SpecsProbe.exe", which is used
with the SPM 150 Aarhus by SPECS.


Installing
----------

Installation via `pip`_:

.. code-block:: bash

    $ pip install mulfile

.. _pip: https://pip.pypa.io/en/stable/


Example Usage
-------------

.. code-block:: python

    import mulfile as mul


    # load a mul or flm file
    stm_images = mul.load('path/to/mulfile.mul')


This returns all STM-images and their metadata as a list-like object.
Thus, it is possible to access images by indexing and slicing.

.. code-block:: python

    # get the first STM-image
    image_1 = stm_images[0]

    # get images 1 to 5
    images = stm_images[0:5]


Single STM-images are stored in objects with their image data (2D numpy array)
and metadata as `attributes`_.

.. _attributes: https://github.com/matkrin/mulfile/wiki

.. code-block:: python

    # get the image data for image_1
    image_1.img_data

    # get the bias voltage for image_1
    image_1.bias


It is also possible to save one or multiple images in the native file format
of `gwyddion`_ (.gwy)

.. code-block:: python

    # save the complete mul-file as a gwyddion file
    stm_images.save_gwy('output.gwy')


.. _gwyddion: http://gwyddion.net/documentation/user-guide-en/gwyfile-format.html


Status
------

STM-images, together with the corresponding metadata, are fully supported  in
both .mul and .flm files. Pointscans are not supported yet.
