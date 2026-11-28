cd /root/stance; export HF_HUB_OFFLINE=1
(CUDA_VISIBLE_DEVICES=0 python model_organism/train.py --data model_organism/data/train_A.jsonl --out model_organism/adapters/A > logs/train_A.log 2>&1; echo "train A exit $?" >> logs/status) &
(CUDA_VISIBLE_DEVICES=1 python model_organism/train.py --data model_organism/data/train_B.jsonl --out model_organism/adapters/B > logs/train_B.log 2>&1; echo "train B exit $?" >> logs/status) &
wait
(CUDA_VISIBLE_DEVICES=0 python model_organism/evalbench.py --label base --out model_organism/results/eval_base.json > logs/eval_base.log 2>&1; echo "eval base exit $?" >> logs/status) &
(CUDA_VISIBLE_DEVICES=1 python model_organism/evalbench.py --label A --adapter model_organism/adapters/A --out model_organism/results/eval_A.json > logs/eval_A.log 2>&1; echo "eval A exit $?" >> logs/status) &
wait
(CUDA_VISIBLE_DEVICES=0 python model_organism/evalbench.py --label B --adapter model_organism/adapters/B --out model_organism/results/eval_B.json > logs/eval_B.log 2>&1; echo "eval B exit $?" >> logs/status) &
(CUDA_VISIBLE_DEVICES=1 python model_organism/neurons.py --adapter model_organism/adapters/A --out model_organism/results/neurons_A.json > logs/neurons_A.log 2>&1; echo "neurons A exit $?" >> logs/status) &
wait
echo ALL_DONE >> logs/status
