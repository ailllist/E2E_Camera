import gc
import torch

gc.collect()
torch.cuda.empty_cache()
torch.cuda.reset_peak_memory_stats()
torch.cuda.caching_allocator_alloc(1024)
# torch.cuda.caching_allocator_alloc(1000000000)

# RuntimeError: CUDA out of memory. Tried to allocate 36.00 MiB (GPU 0; 7.93 GiB total capacity; 130.35 MiB already
# allocated; 47.06 MiB free; 188.00 MiB reserved in total by PyTorch) If reserved memory is >> allocated memory try
# setting max_split_size_mb to avoid fragmentation.
# See documentation for Memory Management and PYTORCH_CUDA_ALLOC_CONF
