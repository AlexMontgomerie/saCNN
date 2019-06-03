from encoding import *
import random

#random.seed(127232)

TEST_SIZE=10

model_path     = 'model/alexnet.prototxt'
model_path     = 'model/vgg16.prototxt'
#model_path     = 'model/lenet.prototxt'
data_path_root = 'data/imagenet'
#data_path_root = 'data/mnist'
weights_path   = 'weight/alexnet.caffemodel'
weights_path   = 'weight/vgg16.caffemodel'
#weights_path   = 'weight/lenet.caffemodel'

# Initialise Network
net = caffe.Classifier(model_path,weights_path)

# get all Images
data_files = []
index=0
for (dirpath, dirnames, filenames) in os.walk(data_path_root):
    for filename in filenames:
        data_files.append(dirpath+'/'+filename)


random_data_files = [ random.choice(data_files) for x in range(TEST_SIZE) ]

# save values for each layer
pixels = {}

# run network
print("RUNNING NETWORK")
for f in random_data_files:
    run_net(net,f)
    # store data
    for layer in net.blobs:
        layer_type = re.match("[a-z]+",str(layer))
        layer_type = layer_type.group(0)
        if layer_type=='conv' or layer_type=='pool' or layer_type=='data':
            print(net.blobs[layer].data.shape)
            if layer in pixels:
                pixels[layer] = np.concatenate( [ pixels[layer], layer_to_stream(net.blobs[layer].data[0][...] ) ] )
            else:
                pixels[layer] = layer_to_stream(net.blobs[layer].data[0][...])


base_sa = {}

# get baseline switching activity
print("BASELINE SA")
for layer in pixels:
    base_sa[layer] = get_sa_stream_avg(pixels[layer])
    print("{layer} switching activity: \t {sa}".format(layer=layer, sa=base_sa[layer]) )

'''
# gray encoding
pixels_gray_encoding = {}
for layer in pixels:
    pixels_gray_encoding[layer] = gray_encoding_stream( pixels[layer] )
    #print(pixels_gray_encoding[layer])
    print("{layer} switching activity (gray encoding): \t {sa}".format( layer=layer, sa=get_sa_stream_avg(pixels_gray_encoding[layer]) ) )

'''
# adaptive encoding (static)
print("BUS INVERT")
bus_invert_encoded = {}
for layer in pixels:
    bus_invert_encoded[layer] = bus_invert_stream( pixels[layer] )
    sa_avg = get_sa_stream_avg(bus_invert_encoded[layer])
    print("{layer} switching activity (bus invert): \t {sa}, reduction = {reduction}".format(
        layer=layer, sa=sa_avg, reduction= (sa_avg/base_sa[layer])*100 ) )


# adaptive encoding (static)
print("ADAPTIVE ENCODING STATIC")
pixels_adaptive_encoding_static = {}
for layer in pixels:
    pixels_adaptive_encoding_static[layer], code_table = adaptive_encoding_static_stream( pixels[layer] )
    sa_avg = get_sa_stream_avg(pixels_adaptive_encoding_static[layer])
    print("{layer} switching activity (adaptive encoding, static): \t {sa} \t (size={size}), reduction = {reduction}".format(
        layer=layer, sa=sa_avg, size=len(code_table), reduction= (sa_avg/base_sa[layer])*100 ) )

'''
# adaptive encoding
pixels_adaptive_encoding = {}
for layer in pixels:
    pixels_adaptive_encoding[layer], _ = adaptive_encoding_stream( pixels[layer] , 500 )
    #print(pixels_gray_encoding[layer])
    print("{layer} switching activity (adaptive encoding, 500): \t {sa}".format( layer=layer, sa=get_sa_stream_avg(pixels_adaptive_encoding[layer]) ) )

'''
'''
DEPTH_MAX = 50
encoded = {}
reduction = {}
for layer in pixels:
    print(layer)
    encoded[layer] = []
    reduction[layer] = []
    for i in range(1,DEPTH_MAX):
        #encoded[layer].append(differential_encoding_stream_2( pixels[layer] , i))
        #sa_avg = get_sa_stream_avg(encoded[layer][i-1])
        sa_avg = get_sa_stream_avg(differential_encoding_stream_2( pixels[layer] , i))
        reduction[layer].append( (sa_avg/base_sa[layer])*100 )

i = 1
for layer in reduction:
    plt.subplot(len(reduction),1,i)
    if i == 1:
        plt.title("Encoded Alexnet Switching Activity Ratio against Offset")
    plt.plot(np.arange(1,DEPTH_MAX),reduction[layer])
    plt.ylabel(layer)
    i+=1
plt.xlabel('offset, k')
plt.show()
'''
'''
pixels_differential_encoding_pure = {}
for layer in pixels:
    pixels_differential_encoding_pure[layer] = differential_encoding_pure_stream( pixels[layer] )
    sa_avg = get_sa_stream_avg(pixels_differential_encoding_pure[layer])
    print("{layer} switching activity (differential encoding pure): \t {sa}, reduction = {reduction}".format(
        layer=layer, sa=sa_avg, reduction = (sa_avg/base_sa[layer])*100 ) )
'''

# differential encoding
print("DIFFERENTIAL ENCODING")
pixels_differential_encoding = {}
offset = {
  "data"  : 3,
  "conv1" : 96,
  "pool1" : 96,
  "conv2" : 256,
  "pool2" : 256,
  "conv3" : 384,
  "conv4" : 384,
  "conv5" : 256,
  "pool5" : 256
}

offsetl = {
  "data"  : 227*3,
  "conv1" : 55*96,
  "pool1" : 27*96,
  "conv2" : 27*256,
  "pool2" : 13*256,
  "conv3" : 13*384,
  "conv4" : 13*384,
  "conv5" : 13*256,
  "pool5" : 6*256
}

offset = {
    "data"    : 3  ,
    "conv1_1" : 64 ,
    "conv1_2" : 64 ,
    "pool1"   : 64 ,
    "conv2_1" : 128,
    "conv2_2" : 128,
    "pool2"   : 128,
    "conv3_1" : 256,
    "conv3_2" : 256,
    "conv3_3" : 256,
    "pool3"   : 256,
    "conv4_1" : 512,
    "conv4_2" : 512,
    "conv4_3" : 512,
    "pool4"   : 512,
    "conv5_1" : 512,
    "conv5_2" : 512,
    "conv5_3" : 512,
    "pool5"   : 512
}

offset4 = {
  "data"  : 1,
  "conv1" : 20,
  "pool1" : 20,
  "conv2" : 50,
  "pool2" : 50
}

for layer in pixels:
    pixels_differential_encoding[layer] = differential_encoding_stream_2( pixels[layer] , offset[layer])
    sa_avg = get_sa_stream_avg(pixels_differential_encoding[layer])
    print("{layer} switching activity (differential encoding): \t {sa}, reduction = {reduction}".format(
        layer=layer, sa=sa_avg, reduction = (sa_avg/base_sa[layer])*100 ) )
    #perform decoding
    #decoded = differential_encoding_stream_2_decode( pixels_differential_encoding[layer] , offset[layer])
    #print(np.linalg.norm(np.subtract(decoded,pixels[layer])))

print("DIFFERENTIAL ENCODING")
pixels_differential_encoding_old = {}
for layer in pixels:
    pixels_differential_encoding_old[layer] = differential_encoding_stream( pixels[layer] , offset[layer])
    sa_avg = get_sa_stream_avg(pixels_differential_encoding_old[layer])
    print("{layer} switching activity (differential encoding old): \t {sa}, reduction = {reduction}".format(
        layer=layer, sa=sa_avg, reduction = (sa_avg/base_sa[layer])*100 ) )
    #perform decoding

######################################################################

'''

block_sizes = [ 25, 50, 75, 100, 150, 200, 250, 500 ]
#block_sizes = [ 500, 1000 ]
switching_activity = {}
mem_size = {}

pixels = {
    'data' : pixels['data']
}

for block_size in block_sizes:
    print('BLOCK_SIZE: ',block_size)
    #for layer in pixels:
    for layer in pixels:
        print(layer)
        encoding, code_table = adaptive_encoding_stream( pixels[layer] , block_size )
        if layer in switching_activity:
            switching_activity[layer].append( get_sa_stream_avg(encoding) )
            mem_size[layer].append( sum([ len(i) for i in code_table ])/TEST_SIZE )
        else:
            switching_activity[layer] = [ get_sa_stream_avg(encoding) ]
            mem_size[layer] = [ sum([ len(i) for i in code_table ])/TEST_SIZE ]


fig, ax1 = plt.subplots()
for layer in pixels:
    ax1.plot(block_sizes,  switching_activity[layer], label=layer, linestyle='--')
ax1.set_xlabel('Block Size')
ax1.set_ylabel('Switching Activity (%)')

ax2 = ax1.twinx()
for layer in pixels:
    ax2.plot(block_sizes, mem_size[layer], label=layer, linestyle='-' )
ax2.set_ylabel('Memory Size')
plt.legend()
plt.grid()
plt.show()

'''
