"""Run the basic and advanced synthetic agent suites without admin mutations."""
import argparse
import agent_suite
import advanced_cases

parser = argparse.ArgumentParser()
parser.add_argument('--model', required=True)
parser.add_argument('--top-p', type=float, default=0.95)
parser.add_argument('--repeats', type=int, default=2)
parser.add_argument('--advanced-repeats', type=int, default=1)
args = parser.parse_args()
if args.repeats < 1 or args.advanced_repeats < 1:
    parser.error('repeat counts must be positive')
agent_suite.run(args.model, args.top_p, repeats=args.repeats)
agent_suite.CASES, agent_suite.TOOLS = advanced_cases.CASES, advanced_cases.TOOLS
agent_suite.run(args.model, args.top_p, repeats=args.advanced_repeats, suffix='-advanced')
