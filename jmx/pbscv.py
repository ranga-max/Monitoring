import json
import csv

def extract_dashboard_panels(dashboard_json_path):
  # Load the Grafana dashboard JSON file
  with open(dashboard_json_path, 'r') as file:
    dashboard = json.load(file)
 
  # Initialize the result structure
  panel_hierarchy = []
 
  # Get all panels from the dashboard
  panels = dashboard.get('panels', [])
 
  # Keep track of the current parent panel
  current_parent = None
  current_children = []
 
  # Process all panels
  for panel in panels:
    panel_type = panel.get('type', '')
   
    # If this is a row panel, it's a parent
    if panel_type == 'row':
      # If we already have a parent with children, add it to the result
      if current_parent and current_children:
        panel_hierarchy.append({
          'parent_panel': current_parent,
          'child_panels': current_children
        })
     
      # Start a new parent
      current_parent = panel.get('title', 'Unnamed Row')
      current_children = []
     
      # Check if row has collapsed panels (nested structure)
      if 'panels' in panel:
        for child_panel in panel.get('panels', []):
          #if child_panel.get('type') in ['stat', 'gauge', 'timeseries', ]:
            metric_info = extract_metric_info(child_panel)
           
            nested_child = {
              'title': child_panel.get('title', 'Unnamed Panel'),
              'type': child_panel.get('type'),
              'metrics': metric_info,
              'description':  child_panel.get('description', 'Unnamed Description')
            }
           
            current_children.append(nested_child)
   
    # If this is not a row and we have a current parent, it's a child panel
    #elif current_parent is not None and panel_type in ['stat', 'gauge', 'timeseries']:
    elif current_parent is not None:    
      metric_info = extract_metric_info(panel)
     
      child_panel = {
        'title': panel.get('title', 'Unnamed Panel'),
        'type': panel_type,
        'metrics': metric_info,
        'description':  panel.get('description', 'Unnamed Description')
      }
     
      current_children.append(child_panel)
 
  # Add the last parent and its children
  if current_parent and current_children:
    panel_hierarchy.append({
      'parent_panel': current_parent,
      'child_panels': current_children
    })
 
  return panel_hierarchy

def extract_metric_info(panel):
  metrics = []
 
  # Handle targets (where Prometheus queries are stored)
  targets = panel.get('targets', [])
 
  for target in targets:
    # Handle simple flat targets
    if 'expr' in target:
      metric_details = {
        'expr': target.get('expr', '')  #, # The Prometheus expression/formula
        #'refId': target.get('refId', ''),
        #'legendFormat': target.get('legendFormat', '')
      }
      metrics.append(metric_details)
   
    # Handle nested targets structure
    elif 'datasource' in target and 'model' in target:
      model = target.get('model', {})
      metric_details = {
        'expr': model.get('expr', '') #, # The Prometheus expression/formula
        #'refId': model.get('refId', '') or target.get('refId', ''),
        #'legendFormat': model.get('legendFormat', '')
      }
      metrics.append(metric_details)
   
    # Handle even more deeply nested targets
    elif isinstance(target, dict):
      # Try to recursively extract any expr fields
      for key, value in target.items():
        if key == 'expr' and isinstance(value, str):
          metric_details = {
            'expr': value,
            #'refId': target.get('refId', '') #,
            #'legendFormat': target.get('legendFormat', '')
          }
          metrics.append(metric_details)
        elif isinstance(value, dict):
          # Look for expr in nested dictionary
          if 'expr' in value:
            metric_details = {
              'expr': value.get('expr', '') #,
              #'refId': value.get('refId', '') or target.get('refId', ''),
              #'legendFormat': value.get('legendFormat', '') or target.get('legendFormat', '')
            }
            metrics.append(metric_details)
 
  return metrics

def extract_metric_name(expression):
    # Find the position of '{job'
    job_pos = expression.find('{job')
    
    if job_pos == -1:
        # '{job' not found in the expression
        return {
            "full_prefix": None,
            "before_last_underscore": None,
            "after_last_underscore": None
        }
    
    # Get the substring before '{job'
    full_prefix = expression[:job_pos]
    jmx_metric_name = ""

    last_paren_pos = full_prefix.rfind('(')
    if last_paren_pos == -1:
        jmx_metric_name = full_prefix
    else:
        jmx_metric_name = full_prefix[last_paren_pos + 1:] 
    
    # Find the last '_' in this substring (going backwards)
    underscore_pos = full_prefix.rfind('_')
    
    if underscore_pos == -1:
        # No '_' found
        return {
            "full_prefix": full_prefix,
            "before_last_underscore": full_prefix,  # Same as full_prefix since there's no '_'
            "after_last_underscore": "",
            "jmx_metric_name": jmx_metric_name
        }
    else:
        return {
            "full_prefix": full_prefix,
            "before_last_underscore": full_prefix[:underscore_pos],
            "after_last_underscore": full_prefix[underscore_pos + 1:], 
            "jmx_metric_name": jmx_metric_name
        }  

def export_to_csv(panel_hierarchy, output_csv_path):
  # Define CSV headers
  headers = ['ParentPanel', 'MetricPanelName', 'MetricType', 'JMXMetricName', 'MetricExpression', 'MetricDescription', 'MetricAttribute']
 
  # Open CSV file for writing
  with open(output_csv_path, 'w', newline='') as csvfile:
    # Create CSV writer with pipe delimiter
    csv_writer = csv.writer(csvfile, delimiter='|')
   
    # Write headers
    csv_writer.writerow(headers)
   
    # Write data rows
    for parent in panel_hierarchy:
      parent_panel_name = parent['parent_panel']
     
      for child in parent['child_panels']:
        child_title = child['title']
        child_type = child['type']
        child_description = child['description']
       
        # If there are no metrics, write one row with empty metric details
        if not child['metrics']:
          csv_writer.writerow([
            parent_panel_name,
            child_title,
            child_type,
            '',
            '',
            '',
            ''
          ])
        else:
          # Write one row for each metric in the child panel
          for metric in child['metrics']:
            exptext = metric.get('expr', '')  
            expression = extract_metric_name(exptext)
            if 'jmx_metric_name' in expression:
                jmx_metric_name = expression['jmx_metric_name']
            else:
                jmx_metric_name = ""
            print(expression['after_last_underscore'])
            csv_writer.writerow([
              parent_panel_name,
              child_title,
              child_type,
              jmx_metric_name,
              metric.get('expr', ''),
              child_description,
              expression['after_last_underscore']
              #text[text.rfind("_", 0, text.find("{job"))]
            ])

def main():
  # Replace with your Grafana dashboard JSON file path
  #dashboard_json_path = '/home/ubuntu/jmx/dashboards/zookeeper-cluster.json'
  #dashboard_json_path = '/home/ubuntu/jmx/dashboards/kafka-cluster.json'
  #dashboard_json_path = '/home/ubuntu/jmx/dashboards/kafka-connect-cluster.json'
  dashboard_json_path = '/home/ubuntu/jmx/dashboards/kafka-topics.json'
  output_csv_path = 'grafana_panels_metrics_topics.csv'
 
  # Extract panel data
  panels = extract_dashboard_panels(dashboard_json_path)
 
  # Print the results in a readable format (optional)
  print(json.dumps(panels, indent=2))
 
  # Export to CSV
  export_to_csv(panels, output_csv_path)
  print(f"CSV file created successfully at: {output_csv_path}")

if __name__ == "__main__":
  main()


