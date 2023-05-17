python run_simulator_sweep.py \
	--dataset helios \
	--cluster_size 16 20 24 28 32 36 40 44 48 \
	52 56 60 64 68 72 76 80 84 88 92 96 100 \
	104 108 112 116 120 124 132 136 140 144 \
	--sched_alg fifo \
	--waiting_policy zero-1 linear_runtime-1.25 \
	--predict_wait 1 \
	--loop 0 1 \
	--seed 1984
