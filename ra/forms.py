from django import forms
from ra.models import RAAppointment, Account, Project, HIRING_CATEGORY_DISABLED, RAAppointmentAttachment, Program
from ra.models import RARequest, RARequestAttachment
from ra.models import DUTIES_CHOICES_EX, DUTIES_CHOICES_DC, DUTIES_CHOICES_PD, DUTIES_CHOICES_IM, DUTIES_CHOICES_EQ
from ra.models import DUTIES_CHOICES_SU, DUTIES_CHOICES_WR, DUTIES_CHOICES_PM
from ra.models import STUDENT_TYPE, GRAS_PAYMENT_METHOD_CHOICES, RA_PAYMENT_METHOD_CHOICES, RA_BENEFITS_CHOICES, BOOL_CHOICES
from django.core.exceptions import ValidationError
from coredata.models import Person, Semester, Unit
from coredata.forms import PersonField
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text



class RARequestForm(forms.ModelForm):
    person = PersonField(label='Appointee')
    supervisor = PersonField(label='Supervisor')

    ra_duties_ex = forms.MultipleChoiceField(required=False, choices=DUTIES_CHOICES_EX, widget=forms.CheckboxSelectMultiple,
                                             label="Experimental/Research Activities")
    ra_duties_dc = forms.MultipleChoiceField(required=False, choices=DUTIES_CHOICES_DC, widget=forms.CheckboxSelectMultiple,
                                             label="Data Collection/Analysis")
    ra_duties_pd = forms.MultipleChoiceField(required=False, choices=DUTIES_CHOICES_PD, widget=forms.CheckboxSelectMultiple,
                                             label="Project Development")
    ra_duties_im = forms.MultipleChoiceField(required=False, choices=DUTIES_CHOICES_IM, widget=forms.CheckboxSelectMultiple,
                                             label="Information Management")
    ra_duties_eq = forms.MultipleChoiceField(required=False, choices=DUTIES_CHOICES_EQ, widget=forms.CheckboxSelectMultiple,
                                             label="Equipment/Inventory Management and Development")
    ra_duties_su = forms.MultipleChoiceField(required=False, choices=DUTIES_CHOICES_SU, widget=forms.CheckboxSelectMultiple,
                                             label="Supervision")
    ra_duties_wr = forms.MultipleChoiceField(required=False, choices=DUTIES_CHOICES_WR, widget=forms.CheckboxSelectMultiple,
                                             label="Writing/Reporting")
    ra_duties_pm = forms.MultipleChoiceField(required=False, choices=DUTIES_CHOICES_PM, widget=forms.CheckboxSelectMultiple,
                                             label="Project Management")    

    people_comments = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':3}), label="Any comments about the Appointee or Hiring Supervisor?")

    student = forms.ChoiceField(required=True, choices=STUDENT_TYPE, widget=forms.RadioSelect, label="Is the appointee a student?")
    coop = forms.ChoiceField(required=False, widget=forms.RadioSelect, choices=BOOL_CHOICES, label="Is the appointee a co-op student?")
    mitacs = forms.ChoiceField(required=False, widget=forms.RadioSelect, choices=BOOL_CHOICES, label="Is the appointee's co-op funded by a Mitacs scholarship in their own name?")
    thesis = forms.ChoiceField(required=False, widget=forms.RadioSelect, choices=BOOL_CHOICES, label="Is the appointment for the student's thesis/project?")

    fs1_unit = forms.IntegerField(required=True, label="Department #1", help_text="CS = 2110; ENSC = 2130; MSE = 2140; SEE = 2150; Dean's Office = 2010, 2020 or 2030")
    fs1_fund = forms.IntegerField(required=True, label="Fund #1", help_text="Example: 11, 13, 21, 31")
    fs1_project = forms.CharField(required=True, label="Project #1", help_text="Example: N654321, S654321, X654321, R654321. If fund 11 enter X000000")
    fs1_percentage = forms.IntegerField(required=False, label="Percentage of Funding Source #1 to Total Funding", help_text="Percentages of all funding sources must add up to 100.")

    fs2_option = forms.BooleanField(required=False, label="Please select the following if there is an additional funding source")
    fs2_unit = forms.IntegerField(required=False, label="Department #2", help_text="CS = 2110; ENSC = 2130; MSE = 2140; SEE = 2150; Dean's Office = 2010, 2020 or 2030")
    fs2_fund = forms.IntegerField(required=False, label="Fund #2", help_text="Example: 11, 13, 21, 31")
    fs2_project = forms.CharField(required=False, label="Project #2", help_text="Example: N654321, S654321, X654321, R654321. If fund 11 enter X000000")
    fs2_percentage = forms.IntegerField(required=False, label="Percentage of Funding Source #2 to Total Funding", help_text="Percentages of all funding sources must add up to 100.")

    fs3_option = forms.BooleanField(required=False, label="Please select the following if there is an additional funding source")
    fs3_unit = forms.IntegerField(required=False, label="Department #3", help_text="CS = 2110; ENSC = 2130; MSE = 2140; SEE = 2150; Dean's Office = 2010, 2020 or 2030")
    fs3_fund = forms.IntegerField(required=False, label="Fund #3", help_text="Example: 11, 13, 21, 31")
    fs3_project = forms.CharField(required=False, label="Percentage #3", help_text="Example: N654321, S654321, X654321, R654321. If fund 11 enter X000000")
    fs3_percentage = forms.IntegerField(required=False, label="Percentage of Funding Source #3 to Total Funding", help_text="Percentages of all funding sources must add up to 100.")

    gras_payment_method = forms.ChoiceField(required=False,
                                            choices=GRAS_PAYMENT_METHOD_CHOICES, 
                                            widget=forms.RadioSelect, 
                                            label="Scholarship (No added benefit & vacation cost)",
                                            help_text='Canadian bank status impacts how students will be paid. This generally applies to International' +
                                            'students currently working outside of Canada, who do not have banking status in Canada. If the status is' + 
                                            'unknown please confirm with the student.')
    ra_payment_method = forms.ChoiceField(required=False, choices=RA_PAYMENT_METHOD_CHOICES, widget=forms.RadioSelect, label="Please select from the following")

    rabw_total_gross = forms.DecimalField(required=False, label="Total Gross Salary Paid", max_digits=8, decimal_places=2)
    rabw_weeks_vacation = forms.DecimalField(required=False, label="Weeks Vacation (Minimum 2)", max_digits=8, decimal_places=1)
    rabw_biweekly_hours = forms.DecimalField(required=False, label="Bi-Weekly Hours", max_digits=8, decimal_places=1)
    rabw_biweekly_salary = forms.DecimalField(required=False, widget=forms.HiddenInput)
    rabw_gross_hourly = forms.DecimalField(required=False, widget=forms.HiddenInput)

    rah_gross_hourly = forms.DecimalField(required=False, label="Gross Hourly", max_digits=8, decimal_places=2)
    rah_vacation_pay = forms.DecimalField(required=False, label="Vacation Pay % (Minimum 4%)", max_digits=8, decimal_places=1)
    rah_biweekly_hours = forms.DecimalField(required=False, label="Bi-Weekly Hours", max_digits=8, decimal_places=2)

    grasls_total_gross = forms.DecimalField(required=False, label="Total Gross Salary Paid", max_digits=8, decimal_places=2)

    grasbw_total_gross = forms.DecimalField(required=False, label="Total Gross Salary Paid", max_digits=8, decimal_places=2)
    grasbw_biweekly_hours = forms.DecimalField(required=False, label="Bi-Weekly Hours", max_digits=8, decimal_places=1)
    grasbw_biweekly_salary = forms.DecimalField(required=False, widget=forms.HiddenInput)
    grasbw_gross_hourly = forms.DecimalField(required=False, widget=forms.HiddenInput)

    ra_benefits = forms.ChoiceField(required=False, choices=RA_BENEFITS_CHOICES, widget=forms.RadioSelect, label="Are you willing to provide extended health benefits?")

    funding_comments = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':3}), label="Any comments about funding?")
    ra_other_duties = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':3}), label="Other RA Duties")


    class Meta:
        model = RARequest
        exclude = ('config','deleted','status',) 
        labels = {
            'first_name': "Appointee First Name",
            'last_name': "Appointee Last Name",
            'email_address': "Appointee Email Address",
            'nonstudent': "Select if appointee does not have an ID",
            'department': "Appointee Department",
            'start_date': "Date Appointment Begins",
            'end_date': "Date Appointment Ends",
            'file_attachment_1': "Supplementary Document #1",
            'file_attachment_2': "Supplementary Document #2",
            }

        widgets = {
            'hiring_category': forms.HiddenInput(),
            'total_pay': forms.HiddenInput()     
        }

        help_texts = {
            'file_attachment_1': "Both of these fields are optional.",
            'file_attachment_2': "If co-op appointment, please upload co-op forms.",
        }

    def __init__(self, *args, **kwargs):
        super(RARequestForm, self).__init__(*args, **kwargs)
        not_required = ['person', 'nonstudent', 'first_name', 'last_name', 'email_address', 'file_attachment_1', 'file_attachment_2',
                    'ra_duties_ex', 'ra_duties_dc', 'ra_duties_pd', 'ra_duties_im', 'ra_duties_eq', 'ra_duties_su', 'ra_duties_wr', 
                    'ra_duties_pm', 'ra_other_duties']
        for field in not_required:
            self.fields[field].required = False   
        
        config_init = ['people_comments', 'coop', 'mitacs', 'student', 'thesis',
                'fs1_unit', 'fs1_fund', 'fs1_project', 'fs1_percentage',
                'fs2_option', 'fs2_unit', 'fs2_fund', 'fs2_project', 'fs2_percentage',
                'fs3_option', 'fs3_unit', 'fs3_fund', 'fs3_project', 'fs3_percentage',
                'rabw_total_gross', 'rabw_weeks_vacation', 'rabw_biweekly_salary', 'rabw_gross_hourly', 'rabw_biweekly_hours',
                'rah_gross_hourly', 'rah_vacation_pay', 'rah_biweekly_hours',
                'grasls_total_gross',
                'grasbw_total_gross', 'grasbw_gross_hourly', 'grasbw_biweekly_hours', 'grasbw_biweekly_salary',
                'ra_payment_method', 'gras_payment_method',
                'ra_benefits', 'funding_comments', 'ra_other_duties']

        for field in config_init:
            self.initial[field] = getattr(self.instance, field)

    def is_valid(self, *args, **kwargs):
        PersonField.person_data_prep(self)
        return super(RARequestForm, self).is_valid(*args, **kwargs)

    # TODO: Make sure total pay and hiring category are calculated properly. Javascript only for now.
    def clean(self):
        cleaned_data = super().clean()

        config_clean = ['people_comments', 'coop', 'mitacs', 'student', 'thesis',
                'fs1_unit', 'fs1_fund', 'fs1_project', 'fs1_percentage',
                'fs2_option', 'fs2_unit', 'fs2_fund', 'fs2_project', 'fs2_percentage',
                'fs3_option', 'fs3_unit', 'fs3_fund', 'fs3_project', 'fs3_percentage',
                'rabw_total_gross', 'rabw_weeks_vacation', 'rabw_biweekly_salary', 'rabw_gross_hourly', 'rabw_biweekly_hours',
                'rah_gross_hourly', 'rah_vacation_pay', 'rah_biweekly_hours',
                'grasls_total_gross',
                'grasbw_total_gross', 'grasbw_gross_hourly', 'grasbw_biweekly_hours', 'grasbw_biweekly_salary',
                'ra_payment_method', 'gras_payment_method',
                'ra_benefits', 'funding_comments', 'ra_other_duties']

        for field in config_clean:
            setattr(self.instance, field, cleaned_data[field])

        MIN_WAGE = 14.60
        MIN_WEEKS_VACATION = 2
        MIN_VACATION_PAY_PERCENTAGE = 4

        nonstudent = cleaned_data.get('nonstudent')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email_address = cleaned_data.get('email_address')
        person = cleaned_data.get('person')

        # TODO: Why isn't this a required field regularly? Not in the list of non-required fields.
        if nonstudent:
            error_message = 'If the appointee does not have an SFU ID then you must answer this question.'       
            if first_name == None:
                self.add_error('first_name', error_message)
            if last_name == None:
                self.add_error('last_name', error_message)
            if email_address == None:
                self.add_error('email_address', error_message)
        else:
            if person == None:
                self.add_error('person', 'You must provide an SFU ID. If the appointee does not have an SFU ID, please select the checkbox below.')

        if nonstudent == None and person == None:
            raise forms.ValidationError("Cannot be a student and not have an SFU ID.")

        student = cleaned_data.get('student')
        coop = cleaned_data.get('coop')
        mitacs = cleaned_data.get('mitacs')
        thesis = cleaned_data.get('thesis')
        if student == 'U' or student == 'M' or student == 'P':
            error_message = 'If the appointee is a student then you must answer this question.'
            if coop == None:
                self.add_error('coop', error_message)
            if mitacs == None:
                self.add_error('mitacs', error_message)
        if mitacs == False:
            if thesis == None:
                self.add_error('thesis', 'You must answer this question.')

        fs2_option = cleaned_data.get('fs2_option')
        fs2_unit = cleaned_data.get('fs2_unit')
        fs2_fund = cleaned_data.get('fs2_fund')
        fs2_project = cleaned_data.get('fs2_project')

        if fs2_option:
            error_message = 'If you have a second funding source then you must answer this question.'
            if fs2_unit == None:
                self.add_error('fs2_unit', error_message)
            if fs2_fund == None:
                self.add_error('fs2_fund', error_message)
            if fs2_project == None or fs2_project == '':
                self.add_error('fs2_project', error_message)

        fs3_option = cleaned_data.get('fs3_option')
        fs3_unit = cleaned_data.get('fs3_unit')
        fs3_fund = cleaned_data.get('fs3_fund')
        fs3_project = cleaned_data.get('fs3_project')

        if fs3_option:
            error_message = 'If you have a third funding source then you must answer this question.'
            if fs3_unit == None:
                self.add_error('fs3_unit', error_message)
            if fs3_fund == None:
                self.add_error('fs3_fund', error_message)
            if fs3_project == None or fs2_project == '':
                self.add_error('fs3_project', error_message)

        fs1_percentage = cleaned_data.get('fs1_percentage')
        fs2_percentage = cleaned_data.get('fs2_percentage')
        fs3_percentage = cleaned_data.get('fs3_percentage')

        error_message = "Combined Percentages of all Funding Sources Must Add Up to 100%"
        if fs2_option and not fs3_option:
            percent_sum = fs1_percentage + fs2_percentage
            if percent_sum != 100:
                self.add_error('fs1_percentage', error_message)
                self.add_error('fs2_percentage', error_message)
        if fs2_option and fs3_option:
            percent_sum = fs1_percentage + fs2_percentage + fs3_percentage
            if percent_sum != 100:
                self.add_error('fs1_percentage', error_message)
                self.add_error('fs2_percentage', error_message)
                self.add_error('fs3_percentage', error_message)

        hiring_category = cleaned_data.get('hiring_category')

        gras_payment_method = cleaned_data.get('gras_payment_method')
        ra_payment_method = cleaned_data.get('ra_payment_method')

        if hiring_category == "RA":
            error_message = "Research Assistants must answer this question."
            if ra_payment_method == None or ra_payment_method == "":
                self.add_error('ra_payment_method', error_message)
        if hiring_category == "GRAS":
            error_message = "Graduate Research Assistants must answer this question."
            if gras_payment_method == None or gras_payment_method == "":
                self.add_error('gras_payment_method', error_message)

        grasbw_total_gross = cleaned_data.get('grasbw_total_gross')
        grasbw_biweekly_hours = cleaned_data.get('grasbw_biweekly_hours')
        grasls_total_gross = cleaned_data.get('grasls_total_gross')
        
        if gras_payment_method:
            error_message = "Graduate Research Assistants must answer this question."
            if gras_payment_method == "LS" or gras_payment_method == "LE":
                if grasls_total_gross == 0 or grasls_total_gross == None:
                    self.add_error('grasls_total_gross', error_message)
            if gras_payment_method == "BW":
                if grasbw_biweekly_hours == 0 or grasbw_biweekly_hours == None:
                    self.add_error('grasbw_biweekly_hours', error_message)
                if grasbw_total_gross == 0 or grasbw_total_gross == None:
                    self.add_error('grasbw_total_gross', error_message)
            if ra_payment_method:
                raise forms.ValidationError("Cannot be both an RA and a GRAS.")

        rabw_total_gross = cleaned_data.get('rabw_total_gross')
        rabw_weeks_vacation = cleaned_data.get('rabw_weeks_vacation')
        rabw_biweekly_hours = cleaned_data.get('rabw_biweekly_hours')
        rah_gross_hourly = cleaned_data.get('rah_gross_hourly')
        rah_vacation_pay = cleaned_data.get('rah_vacation_pay')
        rah_biweekly_hours = cleaned_data.get('rah_biweekly_hours')

        if ra_payment_method:
            error_message = "Research Assistants must answer this question."
            if ra_payment_method == "BW":
                if rabw_total_gross == 0 or rabw_total_gross == None:
                    self.add_error('rabw_total_gross', error_message)
                if rabw_weeks_vacation == None:
                    self.add_error('rabw_weeks_vacation', error_message)
                elif rabw_weeks_vacation < MIN_WEEKS_VACATION:
                    self.add_error('rabw_weeks_vacation', ('Weeks Vacation Must Be At Least ' + str(MIN_WEEKS_VACATION) + ' Weeks'))
                if rabw_biweekly_hours == None or rabw_biweekly_hours == 0:
                    self.add_error('rabw_biweekly_hours', error_message)
            if ra_payment_method == "H":
                if rah_gross_hourly == None:
                    self.add_error('rah_gross_hourly', error_message)
                elif rah_gross_hourly < MIN_WAGE:
                    self.add_error('rah_gross_hourly', ('Gross Hourly Must Be At Least Minimum Wage. (Currently: $' + str(MIN_WAGE) + ')'))
                if rah_vacation_pay == None:
                    self.add_error('rah_vacation_pay', error_message)
                elif rah_vacation_pay < MIN_VACATION_PAY_PERCENTAGE:
                    self.add_error('rah_vacation_pay', ('Vacation Pay Must Be At Least % ' + str(MIN_VACATION_PAY_PERCENTAGE)))
                if rah_biweekly_hours == None or rah_biweekly_hours == 0:
                    self.add_error('rah_biweekly_hours', error_message)

        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if end_date < start_date:
            error_message = "Start date must be before end date."
            self.add_error('end_date', error_message)
            self.add_error('start_date', error_message)

class RARequestNoteForm(forms.ModelForm):
    admin_notes = forms.CharField(required=False, label="Administrative Notes", widget=forms.Textarea)

    class Meta:
        model = RARequest
        fields = ()

    def __init__(self, *args, **kwargs):
        super(RARequestNoteForm, self).__init__(*args, **kwargs)
        config_init = ['admin_notes']

        for field in config_init:
            self.initial[field] = getattr(self.instance, field)

    def clean(self):
        cleaned_data = super().clean()
        config_clean = ['admin_notes']
        for field in config_clean:
            setattr(self.instance, field, cleaned_data[field])

class RARequestAdminForm(forms.ModelForm):
    funding_available = forms.BooleanField(required=False, label="")
    grant_active = forms.BooleanField(required=False, label="")
    salary_allowable = forms.BooleanField(required=False, label="")
    supervisor_check = forms.BooleanField(required=False, label="")
    visa_valid = forms.BooleanField(required=False, label="")
    payroll_collected = forms.BooleanField(required=False, label="")
    paf_signed = forms.BooleanField(required=False, label="")

    class Meta:
        model = RARequest
        fields = ()
    
    def __init__(self, *args, **kwargs):
        super(RARequestAdminForm, self).__init__(*args, **kwargs)
        config_init = ['funding_available', 'grant_active', 'salary_allowable', 'supervisor_check', 'visa_valid',
                        'payroll_collected', 'paf_signed']
        
        for field in config_init:
            self.initial[field] = getattr(self.instance, field)
    
    def clean(self):
        cleaned_data = super().clean()
        config_clean = ['funding_available', 'grant_active', 'salary_allowable', 'supervisor_check', 'visa_valid',
                        'payroll_collected', 'paf_signed']
        for field in config_clean:
            setattr(self.instance, field, cleaned_data[field])
        
class RARequestAdminAttachmentForm (forms.ModelForm):
    class Meta:
        model = RARequestAttachment
        exclude = ('req', 'created_by')

class RAForm(forms.ModelForm):
    person = PersonField(label='Hire')
    sin = forms.IntegerField(label='SIN', required=False)
    use_hourly = forms.BooleanField(label='Use Hourly Rate', initial=False, required=False,
                                    help_text='Should the hourly rate be displayed on the contract (or total hours for lump sum contracts)?')
    
    class Meta:
        model = RAAppointment
        exclude = ('config','offer_letter_text','deleted')

    def __init__(self, *args, **kwargs):
        super(RAForm, self).__init__(*args, **kwargs)
        choices = self.fields['hiring_category'].choices
        choices = [(k,v) for k,v in choices if k not in HIRING_CATEGORY_DISABLED]
        self.fields['hiring_category'].choices = choices

    def is_valid(self, *args, **kwargs):
        PersonField.person_data_prep(self)
        return super(RAForm, self).is_valid(*args, **kwargs)

    def clean_sin(self):
        sin = self.cleaned_data['sin']
        try:
            emplid = int(self['person'].value())
        except ValueError:
            raise forms.ValidationError("The correct format for a SIN is XXXXXXXXX, all numbers, no spaces or dashes.")
        people = Person.objects.filter(emplid=emplid)
        if people:
            person = people[0]
            person.set_sin(sin)
            person.save()
        return sin

    def clean_hours(self):
        data = self.cleaned_data['hours']
        if self.cleaned_data['pay_frequency'] == 'L':
            return data

        if int(data) > 168:
            raise forms.ValidationError("There are only 168 hours in a week.")
        if int(data) < 0:
            raise forms.ValidationError("One cannot work negative hours.")
        return data

    def clean(self):
        cleaned_data = self.cleaned_data
        return cleaned_data 
        

class RALetterForm(forms.ModelForm):
    class Meta:
        model = RAAppointment
        fields = ('offer_letter_text',)
        widgets = {
                   'offer_letter_text': forms.Textarea(attrs={'rows': 25, 'cols': 70}),
                   }


class LetterSelectForm(forms.Form):
    letter_choice = forms.ChoiceField(label='Select a letter', required=True, help_text='Please select the appropriate letter template for this RA.')

    def __init__(self, choices=[], *args, **kwargs):
        super(LetterSelectForm, self).__init__(*args, **kwargs)
        self.fields["letter_choice"].choices = choices


class StudentSelect(forms.TextInput):
    # widget to input an emplid; presumably with autocomplete in the frontend
    pass


class StudentField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        super(StudentField, self).__init__(*args, queryset=Person.objects.none(), widget=StudentSelect(attrs={'size': 20}), help_text="Type to search for a student's appointments.", **kwargs)

    def to_python(self, value):
        try:
            st= Person.objects.get(emplid=value)
        except (ValueError, Person.DoesNotExist):
            raise forms.ValidationError("Unknown person selected")
        return st


class RASearchForm(forms.Form):
    search = StudentField()


class RABrowseForm(forms.Form):
    current = forms.BooleanField(label='Only current appointments', initial=True, help_text='Appointments active now (or within two weeks).')


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        exclude = ('hidden',)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ('hidden',)
        widgets = {
            'project_prefix': forms.TextInput(attrs={'size': 1})
        }


class SemesterConfigForm(forms.Form):
    unit = forms.ModelChoiceField(queryset=Unit.objects.all())
    start_date = forms.DateField(required=True, help_text="Default start date for contracts")
    end_date = forms.DateField(required=True, help_text="Default end date for contracts")


class RAAppointmentAttachmentForm(forms.ModelForm):
    class Meta:
        model = RAAppointmentAttachment
        exclude = ('appointment', 'created_by')


class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        exclude = ('hidden',)
