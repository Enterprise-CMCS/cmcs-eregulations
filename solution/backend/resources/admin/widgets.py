import json

from django.forms.widgets import Textarea


class LocationHistoryWidget(Textarea):
    def locations_to_strings(self, locations):
        strings = []
        for i in locations:
            key = f"{i['type']}_id"
            strings.append(f"{i['title']} CFR {i['part']}.{i[key]}")
        if not strings:
            return None
        if len(strings) == 1:
            return strings[0]
        return ", ".join(strings[0:-1]) + ("," if len(strings) > 2 else "") + f" and {strings[-1]}"

    def format_value(self, value):
        try:
            output = []
            data = json.loads(value)
            if not data:
                return ""
            for i in range(len(data)):
                row = data[i]
                additions = self.locations_to_strings(row["additions"])
                removals = self.locations_to_strings(row["removals"])
                bulk_adds = self.locations_to_strings(row["bulk_adds"])
                date = parse_datetime(row["date"]).strftime("%Y-%m-%d at %I:%M %p")
                output.append(f"{i + 1}: On {date}, {row['user']} %s%s%s%s%s." % (
                    f"added {additions}" if additions else "",
                    " and " if additions and removals else "",
                    f"removed {removals}" if removals else "",
                    " and " if (additions or removals) and bulk_adds else "",
                    f"bulk added {bulk_adds}" if bulk_adds else "",
                ))
            return "\n".join(output)
        except Exception:
            return "Can't render location history."
