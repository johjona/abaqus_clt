# abaqus_clt
![Figure of input dimensions to script](https://github.com/user-attachments/assets/eece4af1-77b7-491b-b499-de734e95daa5)

## Inputs

The following inputs need to be defined:

LayerDict: LayerDict is a Python-dictionary, meaning it has a number of keys to which some corresponding value exists. The key of each indivdual dictionary does not matter but it is proabably reasonable to name the layers in sequential order. The values of different keys are a tuple with 3 elements, such that: dict_value = (layer_height, layer_orientation, layer_material). Here layer_height is the height of the layer and should be a float, layer_orientation denotes if the lamellas should be transversely or longitudinally oriented ("T" or "L"), and is a string. layer_material denotes which material the lamellas in the layer are and is a string. 

Additional inputs are geometrical inputs, see Figure above for definitions of element_width, element_height, and spatial_width. The longitudinal_length and the transversal_length denotes the total length of the panel _excluding_ the spatial width. As such, if a spatial width is used, the total length of the panel will be (longitudinal_length + the sum of all spatial widths in the layer). The element_width needs to be a multiple of both the longitudinal_length and the transversal_length.
 
## Material dictionary
New materials can simply be added to the material dictionary. The key is the name of the material and the value is a tuple with all the elastic constants.

## Methods
The "method"-variable determines how the different layers are constructed. If it is set to "individ" all lamellas are horisontally constrained with a tie constraint in Abaqus. If it is set to "merge" each layer is created by merging all part lamellas in one layer into a new part. At the moment I am unsure how this method is affected if the spatial width is set to non-zero.
