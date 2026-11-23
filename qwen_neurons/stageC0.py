"""Stage C, step 0: unablated first-digit readout on the TRAINING wordings only, to check the readout works. Reads no test prompt."""
from nq import *
J = [j for j in json.load(open("jobsC.json")) if j["split"] == "train"]
for j in J:
    lg = logits(j); top = [tok.decode(t) for t in lg.topk(4).indices.tolist()]; pr = torch.softmax(lg, -1)
    dig = [tid(str(d)) for d in range(10)]
    print(f"{j['anchor']:10s} w{j['wording']} zero-metric {zero_metric(j).item():+.2f} digit-mass {pr[dig].sum().item():.2f} top {top}", flush=True)
