from decimal import Decimal
import json

class TokenTracker:
    
    def __init__(self):
        self.records = []
    
    def add(self, agent_name, input_tokens, output_tokens): 
        self.records.append({
            "agent":  agent_name, #which agent made the call
            "input":  input_tokens, #its input tokens (to sent a prompt)
            "output": output_tokens #tokens in the response we received
        })
    
    def total_tokens(self):
        total = 0
        for record in self.records:
            total += record["input"] + record["output"]
        return total
    
    def cost_usd(self):
        total_input  = sum(r["input"]  for r in self.records)
        total_output = sum(r["output"] for r in self.records)
       
        price_input  = Decimal("0.59")
        price_output = Decimal("0.79")  #prices of groq
        one_million  = Decimal("1000000")
       
        input_cost  = (Decimal(total_input)  / one_million) * price_input
        output_cost = (Decimal(total_output) / one_million) * price_output
        total_cost  = input_cost + output_cost
        
        return float(round(total_cost, 6))

    def cost_inr(self):
        return round(self.cost_usd() * 95.25, 4)

    def agent_breakdown(self):
        breakdown = {}
        
        # Define prices once here as well
        price_input  = Decimal("0.59")
        price_output = Decimal("0.79")
        one_million  = Decimal("1000000")
        
        for record in self.records:
            agent  = record["agent"]
            inp    = record["input"]
            out    = record["output"]
            
            if agent in breakdown:
                breakdown[agent]["input"]  += inp
                breakdown[agent]["output"] += out
            else:
                breakdown[agent] = {
                    "input":  inp,
                    "output": out,
                }
            
           
            total_inp_dec = Decimal(breakdown[agent]["input"])
            total_out_dec = Decimal(breakdown[agent]["output"])
            
            exact_cost = ((total_inp_dec / one_million) * price_input) + ((total_out_dec / one_million) * price_output)
            
            breakdown[agent]["total"]    = breakdown[agent]["input"] + breakdown[agent]["output"]
            breakdown[agent]["cost_usd"] = float(round(exact_cost, 6))
            breakdown[agent]["cost_inr"] = float(round(exact_cost * Decimal('95.25'), 2))
        
        return breakdown    
    
    def summary(self):
        
        exact_usd = Decimal(str(self.cost_usd()))
        conversion_rate = Decimal("95.25")
        exact_inr = exact_usd * conversion_rate

        return {
            "total_tokens":    self.total_tokens(),
            "cost_usd":        self.cost_usd(),
            "cost_inr":        float(round(exact_inr, 2)), 
            "breakdown":       self.records,
            "agent_breakdown": self.agent_breakdown()
        }


#basically a review of employee
class ReviewSession:
    
    def __init__(self, employee_id):
        self.employee_id    = employee_id  
        self.tokens         = TokenTracker() 
        self.final_packet   = None           
        self.human_decision = "pending"      
        self.human_comment  = ""             
    
    def is_complete(self):
       
        return self.human_decision != "pending" 

    def approve(self, comment=""):
        if self.is_complete():
            raise ValueError(
                f"Decision already recorded as '{self.human_decision}'.  "
                f"Cannot change a final decision."
            )
        self.human_decision = "approved"
        self.human_comment  = comment

    def reject(self, comment=""):
        if self.is_complete():
            raise ValueError(
            f"Decision already recorded as '{self.human_decision}'. "
            f"Cannot change a final decision."
        )
        self.human_decision = "rejected"
        self.human_comment  = comment
    
    
    
    def summary(self):
        return {
            "employee_id":    self.employee_id,
            "human_decision": self.human_decision,
            "human_comment":  self.human_comment,
            "ai_decision":    self.final_packet.get("decision") if self.final_packet else None,
            "confidence":     self.final_packet.get("confidence") if self.final_packet else None,
            "token_usage":    self.tokens.summary()
        }





def make_sse_message(agent, status, message, data=None):
    payload = {
        "agent":   agent,
        "status":  status,
        "message": message,
        "data":    data
    }
    
    
    return f"data: {json.dumps(payload)}\n\n"



if __name__ == "__main__":  
    
    tracker = TokenTracker() 
    tracker.add("advocate",     400, 300)
    tracker.add("evaluator",    600, 200)
    tracker.add("evaluator",     800,200)
    tracker.add("orchestrator", 500, 350)
    
    print("Token Summary")
    print(tracker.summary())
    
    
    session = ReviewSession("E1042")
    session.tokens.add("advocate", 400, 300)
    session.tokens.add("evaluator", 400, 300)
    session.final_packet = {"decision": "RECOMMEND", "confidence": 88}
    session.approve("Strong candidate, approve!")
    
    print("\n=== Session Summary ===")
    print(session.summary())
    
    
    msg = make_sse_message("advocate", "running", "Building promotion case...")
    print("\n=== SSE Message ===")
    print(repr(msg))
    

    print("\n=== Per Agent Breakdown ===")
    for agent, usage in tracker.agent_breakdown().items():
        print(f"{agent:15} → input: {usage['input']:4} | output: {usage['output']:4} | cost: ${usage['cost_usd']}")

    print(f"\n=== Total ===")
    print(f"Tokens: {tracker.total_tokens()}")
    print(f"Cost:   ${tracker.cost_usd()}")
